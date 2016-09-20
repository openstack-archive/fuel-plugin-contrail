#!/usr/bin/python
#    Copyright 2016 Mirantis, Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import sys
import atexit
import random
import yaml
import os.path
import argparse
import logging

from pyVim import connect
from pyVmomi import vim
from pyVmomi import vmodl

from nailgun import objects


class Vcenter_base(object):
    def __init__(self, user_data=None, si=None):
        if user_data:
            self.vc_ip = user_data['vcenter_ip']
            self.vc_user = user_data['vcenter_user']
            self.vc_pass = user_data['vcenter_password']
        elif si:
            self.service_instance = si
            self.content = self.service_instance.RetrieveContent()
            self.datacenter = self.content.rootFolder.childEntity[0]
            self.network_folder = self.datacenter.networkFolder
        else:
            logger.error('Need to specify credential for vcenter (user_data) or service instance object (si)')

    def connect_to_vcenter(self):
        """Create connection for vCenter instance"""
        self.service_instance = connect.SmartConnect(host=self.vc_ip,
                                                     user=self.vc_user,
                                                     pwd=self.vc_pass,
                                                     port=443)
        self.content = self.service_instance.RetrieveContent()
        self.datacenter = self.content.rootFolder.childEntity[0]
        self.network_folder = self.datacenter.networkFolder
        atexit.register(connect.Disconnect, self.service_instance)
        return self.service_instance

    def wait_for_tasks(self, service_instance, tasks):
        """Given the service instance si and tasks,

        it returns after all the tasks are complete
        """
        property_collector = service_instance.content.propertyCollector
        task_list = [str(task) for task in tasks]
        # Create filter
        obj_specs = [vmodl.query.PropertyCollector.ObjectSpec(obj=task)
                     for task in tasks]
        property_spec = vmodl.query.PropertyCollector.PropertySpec(type=vim.Task,
                                                                   pathSet=[],
                                                                   all=True)
        filter_spec = vmodl.query.PropertyCollector.FilterSpec()
        filter_spec.objectSet = obj_specs
        filter_spec.propSet = [property_spec]
        pcfilter = property_collector.CreateFilter(filter_spec, True)
        try:
            version, state = None, None
            # Loop looking for updates till the state moves to a completed state.
            while len(task_list):
                update = property_collector.WaitForUpdates(version)
                for filter_set in update.filterSet:
                    for obj_set in filter_set.objectSet:
                        task = obj_set.obj
                        for change in obj_set.changeSet:
                            if change.name == 'info':
                                state = change.val.state
                            elif change.name == 'info.state':
                                state = change.val
                            else:
                                continue

                            if not str(task) in task_list:
                                continue

                            if state == vim.TaskInfo.State.success:
                                # Remove task from taskList
                                task_list.remove(str(task))
                            elif state == vim.TaskInfo.State.error:
                                raise task.info.error
                # Move to next version
                version = update.version
        finally:
            if pcfilter:
                pcfilter.Destroy()

    def get_obj(self, vimtype, name):
        """Get the vsphere object associated with a given text name"""
        obj = None
        container = self.content.viewManager.CreateContainerView(self.content.rootFolder, vimtype, True)
        for c in container.view:
            if c.name == name:
                obj = c
                break
        return obj

    def get_all_hosts(self):
        host_list = list()
        for cl in self.datacenter.hostFolder.childEntity:
            for h in cl.host:
                host = h.name
                host_list.append(host)
        return host_list

    def gen_mac(self):
        """Generate mac address"""
        mac = [0x00, 0x16, 0x3e,
               random.randint(0x00, 0x7f),
               random.randint(0x00, 0xff),
               random.randint(0x00, 0xff)]
        return ':'.join(map(lambda x: "%02x" % x, mac))

    def get_host_ip_by_name(self, name):
        host_obj = self.get_obj([vim.HostSystem], name)
        host_ip = host_obj.config.vmotion.ipConfig.ipAddress
        return host_ip

    def fetch_hosts_data(self):
        hosts_data = list()
        for cl in self.datacenter.hostFolder.childEntity:
            for h in cl.host:
                host_name = h.name
                host_ip = h.config.vmotion.ipConfig.ipAddress
                mac_for_vm = self.gen_mac()
                hosts_data.append({'host': host_name, 'host_ip': host_ip, 'mac_for_vm': mac_for_vm})
        return hosts_data

    @staticmethod
    def get_args():
        """Parse command line arguments"""
        parser = argparse.ArgumentParser()
        parser.add_argument(
            '--env_id', type=int, help='Environment id', required=True)
        parser.add_argument(
            '--spawn', action='store_true', dest='spawn', default=None, help='Spawn vm\'s for contrail-vmware role',
            required=False)
        parser.add_argument(
            '--map-ips', action='store_true', dest='map_ips', default=None, help='Map vmware vm\'s to fuel admin ip\'s',
            required=False)
        parser.add_argument(
            '--dvs-mtu-ext', type=int, dest='dvs_mtu_ext', help='Max MTU for external DVS', default=None)
        parser.add_argument(
            '--dvs-mtu-priv', type=int, dest='dvs_mtu_priv', help='Max MTU for private DVS', default=None)
        parser.add_argument(
            '--dvs-mtu-int', type=int, dest='dvs_mtu_int', help='Max MTU for internal DVS', default=None)
        parser.add_argument(
            '--reduce-vm-params', action='store_true', dest='reduce_vm_params',
            help='Reduce memory value for ContrailVM\'s', default=None)

        args = parser.parse_args()
        return args

    @staticmethod
    def get_vcenter_credentials(cluster_id):
        """Fetch vCenter credential from nailgun

        :param cluster_id: Fuel environment id
        """
        cl = objects.Cluster.get_by_uid(cluster_id)
        if cl:
            vmware_settings = objects.Cluster.get_vmware_attributes(cl).get('editable')
            vcenter_host = vmware_settings['value']['availability_zones'][0].get('vcenter_host')
            vcenter_username = vmware_settings['value']['availability_zones'][0].get('vcenter_username')
            vcenter_password = vmware_settings['value']['availability_zones'][0].get('vcenter_password')
            if not vcenter_host or not vcenter_username or not vcenter_password:
                logger.error('Credentials for vcenter not specified fully. Specify their in Fuel vmware tab.')
                sys.exit(1)
            return vcenter_host, vcenter_username, vcenter_password
        else:
            logger.error('Could not find cluster with ID: {}'.format(cluster_id))
            sys.exit(1)

    @staticmethod
    def get_contrail_settings(cluster_id, setting_name):
        """Fetch Contrail settings from nailgun

        :param cluster_id: Fuel environment id
        :param setting_name: Fuel Contrail setting name
        """
        cl = objects.Cluster.get_by_uid(cluster_id)
        contrail_setting = objects.Cluster.get_editable_attributes(cl)['contrail'].get(setting_name)
        if contrail_setting:
            value = contrail_setting['value']
            return value
        else:
            logger.error('Contrail setting {} does not exist'.format(setting_name))
            sys.exit(1)

    @staticmethod
    def create_logger():
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        ch.setFormatter(formatter)
        logger.addHandler(ch)
        return logger


class Vcenter_obj_tpl(object):
    def controller_info(self):
        scsi_spec = vim.vm.device.VirtualDeviceSpec()
        scsi_spec.operation = vim.vm.device.VirtualDeviceSpec.Operation.add
        scsi_spec.device = vim.vm.device.VirtualLsiLogicController()
        scsi_spec.device.deviceInfo = vim.Description()
        scsi_spec.device.slotInfo = vim.vm.device.VirtualDevice.PciBusSlotInfo()
        scsi_spec.device.slotInfo.pciSlotNumber = 16
        scsi_spec.device.controllerKey = 100
        scsi_spec.device.unitNumber = 3
        scsi_spec.device.busNumber = 0
        scsi_spec.device.hotAddRemove = True
        scsi_spec.device.sharedBus = 'noSharing'
        scsi_spec.device.scsiCtlrUnitNumber = 7
        return scsi_spec

    def disk_info(self, disk_size, controller_info, unit_number=0):
        new_disk_kb = int(disk_size) * 1024 * 1024
        disk_spec = vim.vm.device.VirtualDeviceSpec()
        disk_spec.fileOperation = "create"
        disk_spec.operation = vim.vm.device.VirtualDeviceSpec.Operation.add

        disk_spec.device = vim.vm.device.VirtualDisk()
        disk_spec.device.backing = vim.vm.device.VirtualDisk.FlatVer2BackingInfo()
        disk_spec.device.backing.diskMode = 'persistent'
        disk_spec.device.unitNumber = unit_number
        disk_spec.device.capacityInKB = new_disk_kb
        disk_spec.device.controllerKey = controller_info.device.key
        return disk_spec

    def nic_info(self, nic_type='Vmxnet3', mac_address=None, label=None, dv_pg_obj=None):
        nic_spec = vim.vm.device.VirtualDeviceSpec()
        nic_spec.operation = vim.vm.device.VirtualDeviceSpec.Operation.add
        if nic_type == 'Vmxnet3':
            nic_spec.device = vim.vm.device.VirtualVmxnet3()
        elif nic_type == 'E1000':
            nic_spec.device = vim.vm.device.VirtualE1000()
        if mac_address:
            nic_spec.device.macAddress = mac_address
        nic_spec.device.deviceInfo = vim.Description()
        nic_spec.device.connectable = vim.vm.device.VirtualDevice.ConnectInfo()
        nic_spec.device.connectable.startConnected = True
        nic_spec.device.connectable.allowGuestControl = True
        nic_spec.device.connectable.connected = True
        nic_spec.device.wakeOnLanEnabled = True
        nic_spec.device.addressType = 'assigned'
        if label:
            nic_spec.device.deviceInfo.label = label
        port = vim.dvs.PortConnection()
        # port.switchUuid = '54 01 36 50 13 35 cf f0-3d ad c9 74 36 95 2f 7e'
        # port.portgroupKey = 'dvportgroup-43'
        if dv_pg_obj:
            port.portgroupKey = dv_pg_obj.key
            port.switchUuid = dv_pg_obj.config.distributedVirtualSwitch.uuid
        nic_spec.device.backing = vim.vm.device.VirtualEthernetCard.DistributedVirtualPortBackingInfo()
        nic_spec.device.backing.port = port
        return nic_spec

    def vmx_file_info(self, storage_name, vm_name):
        datastore_path = '[' + storage_name + '] ' + vm_name
        vmx_file = vim.vm.FileInfo(logDirectory=None,
                                   snapshotDirectory=None,
                                   suspendDirectory=None,
                                   vmPathName=datastore_path)
        return vmx_file

    def dvs_info(self, dvs_name, private_vlan=None, max_mtu=None):
        pvlan_configs = []
        dvs_create_spec = vim.DistributedVirtualSwitch.CreateSpec()
        dvs_config_spec = vim.dvs.VmwareDistributedVirtualSwitch.ConfigSpec()
        if private_vlan:
            for pvlan_idx in range(100, 2001, 2):
                # promiscuous  pvlan config
                pvlan_map_entry = vim.dvs.VmwareDistributedVirtualSwitch.PvlanMapEntry()
                pvlan_config_spec = vim.dvs.VmwareDistributedVirtualSwitch.PvlanConfigSpec()
                pvlan_map_entry.primaryVlanId = pvlan_idx
                pvlan_map_entry.secondaryVlanId = pvlan_idx
                pvlan_map_entry.pvlanType = "promiscuous"
                pvlan_config_spec.pvlanEntry = pvlan_map_entry
                pvlan_config_spec.operation = vim.ConfigSpecOperation.add
                # isolated pvlan config
                pvlan_map_entry2 = vim.dvs.VmwareDistributedVirtualSwitch.PvlanMapEntry()
                pvlan_config_spec2 = vim.dvs.VmwareDistributedVirtualSwitch.PvlanConfigSpec()
                pvlan_map_entry2.primaryVlanId = pvlan_idx
                pvlan_map_entry2.secondaryVlanId = pvlan_idx + 1
                pvlan_map_entry2.pvlanType = "isolated"
                pvlan_config_spec2.pvlanEntry = pvlan_map_entry2
                pvlan_config_spec2.operation = vim.ConfigSpecOperation.add
                pvlan_configs.append(pvlan_config_spec)
                pvlan_configs.append(pvlan_config_spec2)
            dvs_config_spec.pvlanConfigSpec = pvlan_configs
        dvs_config_spec.name = dvs_name
        if max_mtu:
            dvs_config_spec.maxMtu = int(max_mtu)
        dvs_create_spec.configSpec = dvs_config_spec
        return dvs_create_spec

    def dvs_host_info(self, host, uplink=None):
        dvs_host_configs = list()
        uplink_port_names = 'dvUplink1'
        dvs_config_spec = vim.DistributedVirtualSwitch.ConfigSpec()
        dvs_config_spec.uplinkPortPolicy = vim.DistributedVirtualSwitch.NameArrayUplinkPortPolicy()
        dvs_config_spec.uplinkPortPolicy.uplinkPortName = uplink_port_names
        dvs_config_spec.maxPorts = 60000
        dvs_host_config = vim.dvs.HostMember.ConfigSpec()
        dvs_host_config.operation = vim.ConfigSpecOperation.add
        dvs_host_config.host = host
        if uplink:
            pnic_specs = list()
            pnic_spec = vim.dvs.HostMember.PnicSpec()
            pnic_spec.pnicDevice = uplink
            pnic_specs.append(pnic_spec)
            dvs_host_config.backing = vim.dvs.HostMember.PnicBacking()
            dvs_host_config.backing.pnicSpec = pnic_specs
        dvs_host_configs.append(dvs_host_config)
        dvs_config_spec.host = dvs_host_configs
        return dvs_config_spec

    def dvs_pg_info(self, dv_pg_name, dv_pg_ports_num, vlan_type, vlan_list):
        dv_pg_spec = vim.dvs.DistributedVirtualPortgroup.ConfigSpec()
        dv_pg_spec.name = dv_pg_name
        dv_pg_spec.numPorts = int(dv_pg_ports_num)
        dv_pg_spec.type = vim.dvs.DistributedVirtualPortgroup.PortgroupType.earlyBinding
        dv_pg_spec.defaultPortConfig = vim.dvs.VmwareDistributedVirtualSwitch.VmwarePortConfigPolicy()
        dv_pg_spec.defaultPortConfig.securityPolicy = vim.dvs.VmwareDistributedVirtualSwitch.SecurityPolicy()
        if vlan_type == 'access':
            dv_pg_spec.defaultPortConfig.vlan = vim.dvs.VmwareDistributedVirtualSwitch.VlanIdSpec()
            dv_pg_spec.defaultPortConfig.vlan.vlanId = vlan_list[0]
        elif vlan_type == 'trunk':
            dv_pg_spec.defaultPortConfig.vlan = vim.dvs.VmwareDistributedVirtualSwitch.TrunkVlanSpec()
            dv_pg_spec.defaultPortConfig.vlan.vlanId = [vim.NumericRange(start=vlan_list[0], end=vlan_list[1])]
        dv_pg_spec.defaultPortConfig.securityPolicy.allowPromiscuous = vim.BoolPolicy(value=True)
        dv_pg_spec.defaultPortConfig.securityPolicy.forgedTransmits = vim.BoolPolicy(value=True)
        dv_pg_spec.defaultPortConfig.vlan.inherited = False
        dv_pg_spec.defaultPortConfig.securityPolicy.macChanges = vim.BoolPolicy(value=False)
        dv_pg_spec.defaultPortConfig.securityPolicy.inherited = False
        return dv_pg_spec

    def startup_info(self, vm_obj, host_obj):
        hostdefsettings = vim.host.AutoStartManager.SystemDefaults()
        hostdefsettings.enabled = True
        hostdefsettings.startDelay = 120
        spec = host_obj.configManager.autoStartManager.config
        spec.defaults = hostdefsettings
        auto_power_info = vim.host.AutoStartManager.AutoPowerInfo()
        auto_power_info.key = vm_obj
        auto_power_info.startAction = 'powerOn'
        auto_power_info.startDelay = -1
        auto_power_info.startOrder = -1
        auto_power_info.stopAction = 'None'
        auto_power_info.stopDelay = -1
        auto_power_info.waitForHeartbeat = 'no'
        spec.powerInfo = [auto_power_info]
        return spec


class Vm(Vcenter_base, Vcenter_obj_tpl):
    def __init__(self, user_data=None, si=None):
        super(Vm, self).__init__(user_data, si)
        self._unit_number = None
        self._nic_unit_number = None
        self.vm_devices = list()
        self.scsi_spec = self.controller_info()
        self.vm_devices.append(self.scsi_spec)

    def add_disk(self, disk_size):
        """Add disk specifications for vm object

        :param disk_size: size of disk in MB
        """
        if self._unit_number >= 0:
            self._unit_number += 1
        else:
            self._unit_number = 0

        disk_spec = self.disk_info(disk_size, self.scsi_spec, self._unit_number)
        self.vm_devices.append(disk_spec)

    def add_nic(self, nic_type='Vmxnet3', mac_address=None, dv_pg_name=None):
        """Add nic specification for vm object

        :param nic_type: type of virtual Ethernet adapter. possible values: Vmxnet3, E1000
        :param mac_address: mac address of virtual Ethernet adapter
        :param dv_pg_name: if set, added nic to given port group
        """
        if self._nic_unit_number >= 0:
            self._nic_unit_number += 1
        else:
            self._nic_unit_number = 0
        label = 'nic' + str(self._nic_unit_number)
        if dv_pg_name:
            dv_pg_obj = self.get_obj([vim.DistributedVirtualPortgroup], dv_pg_name)
            if not dv_pg_obj:
                logger.warning('Port group: {} does not exist.'.format(dv_pg_name))
        else:
            dv_pg_obj = None
        nic_spec = self.nic_info(nic_type, mac_address, label, dv_pg_obj)
        self.vm_devices.append(nic_spec)

    def create(self, name, cpu, memory, storage_name, cluster=None, host=None):
        """Create virtual machine

        :param name: name of virtual machine
        :param cpu: cpu amount
        :param memory: memory amount in MB
        :param storage_name: name of datastore where vm will be spawned
        :param cluster: optional, set cluster where vm will be created
        :param host: optional, set ESXi host where vm will be created
        """
        vm_obj = self.get_obj([vim.VirtualMachine], name)
        if vm_obj:
            logger.info('VM({}) already exist. Skip creation VM: {}.'.format(name, name))
            return vm_obj
        if host:
            host_obj = self.get_obj([vim.HostSystem], host)
            if not host_obj:
                logger.warning('Host({}) does not exist. Skip creation VM: {}.'.format(host, name))
                return
            if not any(ds.name == storage_name for ds in host_obj.datastore):
                logger.warning(
                    'Datastore({}) does not exist on Host({}). Skip creation VM: {}.'.format(storage_name, host, name))
                return
            vm_folder = host_obj.parent.parent.parent.vmFolder
            resource_pool = host_obj.parent.resourcePool
        elif cluster:
            host_obj = None
            cluster_obj = self.get_obj([vim.ClusterComputeResource], cluster)
            if not cluster_obj:
                logger.warning('Cluster({}) does not exist. Skip creation VM: {}.'.format(cluster, name))
                return
            if not any(ds.name == storage_name for ds in cluster_obj.datastore):
                logger.warning(
                    'Datastore({}) does not exist on Cluster({}). Skip creation VM: {}.'.format(storage_name, cluster,
                                                                                                name))
                return
            vm_folder = cluster_obj.parent.parent.vmFolder
            resource_pool = cluster_obj.resourcePool
        else:
            logger.error(
                'Need to specify Cluster or Host name where you want to create vm. Skip creation VM: {}.'.format(name))
            return

        vmx_file = self.vmx_file_info(storage_name, name)

        self.config = vim.vm.ConfigSpec(
            name=name,
            memoryMB=memory,
            numCPUs=cpu,
            guestId="ubuntu64Guest",
            files=vmx_file,
            deviceChange=self.vm_devices,
        )

        logger.info('Creating VM {}...'.format(name))

        task = vm_folder.CreateVM_Task(config=self.config, pool=resource_pool, host=host_obj)
        self.wait_for_tasks(self.service_instance, [task])

    def power_on(self, name):
        """Power on virtual machine

        :param name: name of virtual machine
        """
        vm_obj = self.get_obj([vim.VirtualMachine], name)
        if not vm_obj:
            logger.error('VM({}) does not exist. Skip power on VM: {}.'.format(name, name))
            return
        if vm_obj.summary.runtime.powerState == 'poweredOn':
            logger.info('VM({}) already power on. Skip power on VM: {}.'.format(name, name))
            return
        task = vm_obj.PowerOnVM_Task()
        self.wait_for_tasks(self.service_instance, [task])

    def enable_startup(self, name):
        """Enable startup for virtual machine

        :param name:  name of virtual machine
        """
        vm_obj = self.get_obj([vim.VirtualMachine], name)
        if not vm_obj:
            logger.error('VM({}) does not exist. Skip adding to startup VM: {}.'.format(name, name))
            return
        host_obj = vm_obj.summary.runtime.host
        power_info = host_obj.configManager.autoStartManager.config.powerInfo
        if not host_obj:
            logger.warning('Host({}) does not exist. Skip adding to startup VM: {}.'.format(host_obj.name, name))
            return
        if any(pf.key == vm_obj for pf in power_info):
            logger.info('VM({}) already added to startup. Skip adding to startup VM: {}.'.format(name, name))
        spec = self.startup_info(vm_obj, host_obj)
        host_obj.configManager.autoStartManager.ReconfigureAutostart(spec)
        logger.info('Enable startup for VM: {}'.format(name))


class Dvs(Vcenter_base, Vcenter_obj_tpl):
    def create(self, dvs_name, private_vlan, max_mtu=None):
        """Create Distributed Virtual Switch

        :param dvs_name: name of switch
        :param private_vlan: if set, configure private VLAN range
        """
        dvs_obj = self.get_obj([vim.DistributedVirtualSwitch], dvs_name)
        if dvs_obj:
            logger.info('DVS({}) already exist. Skip creation DVS: {}.'.format(dvs_name, dvs_name))
            return dvs_obj
        dvs_spec = self.dvs_info(dvs_name, private_vlan, max_mtu)
        logger.info('Creating DVS {}...'.format(dvs_name))
        task = self.network_folder.CreateDVS_Task(dvs_spec)
        self.wait_for_tasks(self.service_instance, [task])

    def add_hosts(self, hosts_list, dvs_name, attach_uplink):
        """Add ESXi hosts to Distributed Virtual Switch

        :param hosts_list: list of hosts with uplink relation. Example: [{'host': '192.168.0.100', 'uplink': 'vmnic1'},]
        :param dvs_name: name of Distributed Virtual Switch
        :param attach_uplink: if set, attach host with uplink to DVS
        """
        dvs_obj = self.get_obj([vim.DistributedVirtualSwitch], dvs_name)
        if not dvs_obj:
            logger.warning('DVS({}) does not exist. Skip adding Hosts: {}.'.format(dvs_name, str(hosts_list)))
            return
        for h in hosts_list:
            host = h['host']
            uplink = h['uplink']
            if any(dvs_host.config.host.name == host for dvs_host in dvs_obj.config.host):
                logger.info(
                    'Host({}) already adding to DVS({}). Skip adding Host: {}.'.format(host, dvs_name, host))
                continue
            if not attach_uplink:
                uplink = None
            host_obj = self.get_obj([vim.HostSystem], host)
            dvs_host_spec = self.dvs_host_info(host_obj, uplink)
            dvs_host_spec.configVersion = dvs_obj.config.configVersion
            logger.info('Adding {} to DVS: {}'.format(host, dvs_name))
            task = dvs_obj.ReconfigureDvs_Task(dvs_host_spec)
            self.wait_for_tasks(self.service_instance, [task])


class Dvpg(Vcenter_base, Vcenter_obj_tpl):
    def create(self, dvs_name, dv_pg_ports_num=128, dv_pg_name=None, vlan_type='access', vlan_list=[0]):
        """Create Distributed Virtual Port Group

        :param dvs_name: name of DVS where DVPG will be created
        :param dv_pg_ports_num: number of ports in DVPG
        :param dv_pg_name: name of Distributed Virtual Port Group
        :param vlan_type: vlan type, possible values: trunk, access
        :param vlan_list: range of vlans that will be set, for vlan_type 'access' will take first element of list,
        for vlan_type 'trunk' need set 2 values: first and last value of range
        """
        if not dv_pg_name:
            dv_pg_name = dvs_name + '-PG'
        dvs_obj = self.get_obj([vim.DistributedVirtualSwitch], dvs_name)
        if not dvs_obj:
            logger.warning('DVS({}) does not exist. Skip creation DVS-PG: {}.'.format(dvs_name, dv_pg_name))
            return
        dv_pg_obj = self.get_obj([vim.dvs.DistributedVirtualPortgroup], dv_pg_name)
        if dv_pg_obj:
            logger.info('DVS-PG({}) already exist. Skip creation DVS-PG: {}.'.format(dv_pg_name, dv_pg_name))
            return
        dv_pg_spec = self.dvs_pg_info(dv_pg_name, dv_pg_ports_num, vlan_type, vlan_list)
        logger.info('Adding PG: {} to DVS: {}'.format(dv_pg_name, dvs_name))
        task = dvs_obj.AddDVPortgroup_Task([dv_pg_spec])
        self.wait_for_tasks(self.service_instance, [task])


class Vcenterdata(object):
    def __init__(self, file_name):
        self.file = file_name
        self.data_key = 'contrail_esxi_info'
        self.old_data = None

    def exists(self):
        """Check if file exists"""
        if os.path.exists(self.file):
            return True
        else:
            logger.info('File: {} does not exist'.format(self.file))
            return False

    def put(self, data):
        """Save data in given file

        :param data: data to save
        """
        if self.exists():
            with open(self.file, 'r+') as f:
                content = yaml.load(f.read())
                f.seek(0)
                for d in data:
                    if not any(old_d['host'] == d['host'] for old_d in content[self.data_key]):
                        content[self.data_key].append(d)
                yaml.dump(content, f, default_flow_style=False, explicit_start=True)
        else:
            with open(self.file, 'w') as f:
                content = {self.data_key: data}
                yaml.dump(content, f, default_flow_style=False, explicit_start=True)

    def get(self):
        """Get data from given file"""
        if self.exists():
            with open(self.file) as f:
                content = yaml.load(f.read())
                return content[self.data_key]

    def add_admin_ip(self):
        """Append file with a ip's from admin fuel network"""
        if self.exists():
            with open(self.file, 'r+') as f:
                content = yaml.load(f.read())
                f.seek(0)
                for i, v in enumerate(content[self.data_key]):
                    mac = v['mac_for_vm']
                    node_obj = objects.Node.get_by_mac_or_uid(mac=mac)
                    if not node_obj:
                        logger.warning('Node with mac: {} not found.'.format(mac))
                        continue
                    admin_ip = node_obj.ip
                    content[self.data_key][i]['admin_ip'] = admin_ip
                yaml.dump(content, f, default_flow_style=False, explicit_start=True)


if __name__ == '__main__':
    logger = Vcenter_base.create_logger()
    # Parse parameter from command line
    args = Vcenter_base.get_args()
    env_id = args.env_id
    dvs_mtu_ext = args.dvs_mtu_ext
    dvs_mtu_priv = args.dvs_mtu_priv
    dvs_mtu_int = args.dvs_mtu_int
    # Get credential to vCenter from Fuel vmware tab
    vcenter_host, vcenter_username, vcenter_password = Vcenter_base.get_vcenter_credentials(env_id)
    user_data = {'vcenter_ip': vcenter_host, 'vcenter_user': vcenter_username, 'vcenter_password': vcenter_password}
    # Get settings from Fuel contrail section
    dvs_external = Vcenter_base.get_contrail_settings(env_id, 'dvs_external')
    dvs_internal = Vcenter_base.get_contrail_settings(env_id, 'dvs_internal')
    dvs_private = Vcenter_base.get_contrail_settings(env_id, 'dvs_private')
    dvpg_external = dvs_external + '-PG'
    dvpg_internal = dvs_internal + '-PG'
    dvpg_private = dvs_private + '-PG'
    esxi_uplink_ext = Vcenter_base.get_contrail_settings(env_id, 'esxi_uplink_ext')
    esxi_uplink_priv = Vcenter_base.get_contrail_settings(env_id, 'esxi_uplink_priv')
    storage_name = Vcenter_base.get_contrail_settings(env_id, 'esxi_datastore_name')

    vm_disk_size = 20  # GB
    vm_cpu = 3  # Amount
    if args.reduce_vm_params:
        vm_memory = 2048  # MB
    else:
        vm_memory = 8228  # MB

    vcenter_connect = Vcenter_base(user_data)
    si = vcenter_connect.connect_to_vcenter()
    hosts_name = vcenter_connect.get_all_hosts()
    host_list_dvs_ext = [{'host': host, 'uplink': esxi_uplink_ext} for host in hosts_name]
    host_list_dvs_priv = [{'host': host, 'uplink': esxi_uplink_priv} for host in hosts_name]
    host_list_dvs_int = [{'host': host, 'uplink': None} for host in hosts_name]
    vmware_data_new = vcenter_connect.fetch_hosts_data()

    # Specify where save vmware_data
    file_dir = '/var/www/nailgun/plugins/contrail-5.0/deployment_scripts/puppet/modules/contrail/files/'
    file_name = 'vmware_data_{}.yaml'.format(str(env_id))
    vmware_datastore = Vcenterdata(file_dir + file_name)
    if vmware_datastore.exists():
        vmware_data_old = vmware_datastore.get()
        vmware_data = vmware_data_old
        for d in vmware_data_new:
            if not any(old_d['host'] == d['host'] for old_d in vmware_data_old):
                vmware_data.append(d)
    else:
        vmware_data = vmware_data_new
    vmware_datastore.put(vmware_data)

    if args.spawn:
        # Create DVS's and DVPG's
        dvs = Dvs(si=si)
        dvpg = Dvpg(si=si)

        dvs.create(dvs_name=dvs_external, private_vlan=False, max_mtu=dvs_mtu_ext)
        dvs.add_hosts(hosts_list=host_list_dvs_ext, dvs_name=dvs_external, attach_uplink=True)
        dvpg.create(dv_pg_name=dvpg_external, dvs_name=dvs_external, vlan_type='trunk', vlan_list=[0, 4094])

        dvs.create(dvs_name=dvs_internal, private_vlan=True, max_mtu=dvs_mtu_int)
        dvs.add_hosts(hosts_list=host_list_dvs_int, dvs_name=dvs_internal, attach_uplink=False)
        dvpg.create(dv_pg_name=dvpg_internal, dvs_name=dvs_internal, vlan_type='trunk', vlan_list=[0, 4094])

        dvs.create(dvs_name=dvs_private, private_vlan=False, max_mtu=dvs_mtu_priv)
        dvs.add_hosts(hosts_list=host_list_dvs_priv, dvs_name=dvs_private, attach_uplink=True)
        dvpg.create(dv_pg_name=dvpg_private, dvs_name=dvs_private, vlan_type='trunk', vlan_list=[0, 4094])

        # Create contrail vm on all hosts in datacenter
        for h in vmware_data:
            vm_host = h['host']
            vm_ext_mac = h['mac_for_vm']
            vm_name = 'ContrailVM-' + vm_host
            vm = Vm(si=si)
            # Specify disk for contrail vm
            vm.add_disk(vm_disk_size)
            # Specify network adapter for contrail vm
            vm.add_nic(dv_pg_name=dvpg_external, mac_address=vm_ext_mac)
            vm.add_nic(dv_pg_name=dvpg_private)
            vm.add_nic(dv_pg_name=dvpg_internal)
            vm.create(name=vm_name, cpu=vm_cpu, memory=vm_memory, storage_name=storage_name, host=vm_host)
            vm.enable_startup(vm_name)
            vm.power_on(vm_name)
    elif args.map_ips:
        vmware_datastore.add_admin_ip()

