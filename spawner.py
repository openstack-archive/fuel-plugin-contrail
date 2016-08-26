#!/usr/bin/python
import sys
import atexit

from pyVim import connect
from pyVmomi import vim
from pyVmomi import vmodl


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
            print 'Need to specify credential for vcenter (user_data) or service instance object (si)'

    def connect_to_vcenter(self):
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
        """Given the service instance si and tasks, it returns after all the
       tasks are complete
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
        """
        Get the vsphere object associated with a given text name
        """
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

    def dvs_info(self, dvs_name, private_vlan=None):
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


class Vm(Vcenter_base, Vcenter_obj_tpl):
    def __init__(self, user_data=None, si=None):
        super(Vm, self).__init__(user_data, si)
        self._unit_number = None
        self._nic_unit_number = None
        self.vm_devices = list()
        self.scsi_spec = self.controller_info()
        self.vm_devices.append(self.scsi_spec)

    def add_disk(self, disk_size):
        if self._unit_number >= 0:
            self._unit_number += 1
        else:
            self._unit_number = 0

        disk_spec = self.disk_info(disk_size, self.scsi_spec, self._unit_number)
        self.vm_devices.append(disk_spec)

    def add_nic(self, nic_type='Vmxnet3', mac_address=None, dv_pg_name=None):
        if self._nic_unit_number >= 0:
            self._nic_unit_number += 1
        else:
            self._nic_unit_number = 0
        label = 'nic' + str(self._nic_unit_number)
        if dv_pg_name:
            dv_pg_obj = self.get_obj([vim.DistributedVirtualPortgroup], dv_pg_name)
            if not dv_pg_obj:
                print "Port group: {} does not exist.".format(dv_pg_name)
        else:
            dv_pg_obj = None
        nic_spec = self.nic_info(nic_type, mac_address, label, dv_pg_obj)
        self.vm_devices.append(nic_spec)

    def create(self, name, cpu, memory, storage_name, cluster=None, host=None):
        vm_obj = self.get_obj([vim.VirtualMachine], name)
        if vm_obj:
            print "VM({}) already exist. Skip creation VM: {}.".format(name, name)
            return vm_obj
        if host:
            host_obj = self.get_obj([vim.HostSystem], host)
            if not host_obj:
                print "Host({}) does not exist. Skip creation VM: {}.".format(host, name)
                return
            if not any(ds.name == storage_name for ds in host_obj.datastore):
                print "Datastore({}) does not exist on Host({}). Skip creation VM: {}.".format(storage_name, host, name)
                return
            vm_folder = host_obj.parent.parent.parent.vmFolder
            resource_pool = host_obj.parent.resourcePool
        elif cluster:
            host_obj = None
            cluster_obj = self.get_obj([vim.ClusterComputeResource], cluster)
            if not cluster_obj:
                print "Cluster({}) does not exist. Skip creation VM: {}.".format(cluster, name)
                return
            if not any(ds.name == storage_name for ds in cluster_obj.datastore):
                print "Datastore({}) does not exist on Cluster({}). Skip creation VM: {}.".format(storage_name, cluster,
                                                                                                  name)
                return
            vm_folder = cluster_obj.parent.parent.vmFolder
            resource_pool = cluster_obj.resourcePool
        else:
            print "Need to specify Cluster or Host name where you want to create vm. Skip creation VM: {}.".format(name)
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

        print "Creating VM {}...".format(name)

        task = vm_folder.CreateVM_Task(config=self.config, pool=resource_pool, host=host_obj)
        self.wait_for_tasks(self.service_instance, [task])

    def power_on(self, name):
        vm_obj = self.get_obj([vim.VirtualMachine], name)
        if not vm_obj:
            print "VM({}) does not exist. Skip power on VM: {}.".format(name, name)
            return
        if vm_obj.summary.runtime.powerState == 'poweredOn':
            print "VM({}) already power on. Skip power on VM: {}.".format(name, name)
            return
        task = vm_obj.PowerOnVM_Task()
        self.wait_for_tasks(self.service_instance, [task])


class Dvs(Vcenter_base, Vcenter_obj_tpl):
    def create(self, dvs_name, private_vlan):
        dvs_obj = self.get_obj([vim.DistributedVirtualSwitch], dvs_name)
        if dvs_obj:
            print "DVS({}) already exist. Skip creation DVS: {}.".format(dvs_name, dvs_name)
            return dvs_obj
        dvs_spec = self.dvs_info(dvs_name, private_vlan)
        print "Creating DVS:", dvs_name
        task = self.network_folder.CreateDVS_Task(dvs_spec)
        self.wait_for_tasks(self.service_instance, [task])

    def add_hosts(self, hosts_list, dvs_name, attach_uplink):
        dvs_obj = self.get_obj([vim.DistributedVirtualSwitch], dvs_name)
        if not dvs_obj:
            print "DVS({}) does not exist. Skip adding Hosts: {}.".format(dvs_name, str(hosts_list))
            return
        for h in hosts_list:
            # FIXME it can be implement for all hosts together
            host = h['host']
            uplink = h['uplink']
            if any(dvs_host.config.host.name == host for dvs_host in dvs_obj.config.host):
                print "Host({}) already adding to DVS({}). Skip adding Host: {}.".format(host, dvs_name, host)
                continue
            if not attach_uplink:
                uplink = None
            host_obj = self.get_obj([vim.HostSystem], host)
            dvs_host_spec = self.dvs_host_info(host_obj, uplink)
            dvs_host_spec.configVersion = dvs_obj.config.configVersion
            print "Adding {} to DVS: {}".format(host, dvs_name)
            task = dvs_obj.ReconfigureDvs_Task(dvs_host_spec)
            self.wait_for_tasks(self.service_instance, [task])


class Dvpg(Vcenter_base, Vcenter_obj_tpl):
    def create(self, dvs_name, dv_pg_ports_num=128, dv_pg_name=None, vlan_type='access', vlan_list=[0]):
        if not dv_pg_name:
            dv_pg_name = dvs_name + '-PG'
        dvs_obj = self.get_obj([vim.DistributedVirtualSwitch], dvs_name)
        if not dvs_obj:
            print "DVS({}) does not exist. Skip creation DVS-PG: {}.".format(dvs_name, dv_pg_name)
            return
        dv_pg_obj = self.get_obj([vim.dvs.DistributedVirtualPortgroup], dv_pg_name)
        if dv_pg_obj:
            print "DVS-PG({}) already exist. Skip creation DVS-PG: {}.".format(dv_pg_name, dv_pg_name)
            return
        dv_pg_spec = self.dvs_pg_info(dv_pg_name, dv_pg_ports_num, vlan_type, vlan_list)
        print "Adding PG: {} to DVS: {}".format(dv_pg_name, dvs_name)
        task = dvs_obj.AddDVPortgroup_Task([dv_pg_spec])
        self.wait_for_tasks(self.service_instance, [task])


if __name__ == '__main__':
    user_data = {'vcenter_ip': '172.16.0.145', 'vcenter_user': 'root', 'vcenter_password': 'vmware'}
    dvs_external = 'Contrail-DVS-Ext'
    dvs_internal = 'Contrail-DVS-Int'
    dvpg_external = dvs_external + '-PG'
    dvpg_internal = dvs_internal + '-PG'
    uplink_name = 'vmnic1'
    storage_name = 'nfs'
    vm_disk_size = 20  # GB
    vm_cpu = 2  # Amount
    vm_memory = 1024  # MB

    vcenter_connect = Vcenter_base(user_data)
    si = vcenter_connect.connect_to_vcenter()
    hosts = vcenter_connect.get_all_hosts()
    host_list = [{'host': host, 'uplink': uplink_name} for host in hosts]
    vm = Vm(si=si)
    dvs = Dvs(si=si)
    dvpg = Dvpg(si=si)

    # Create Distributed Switch to connect contrail vm with fuel master node
    dvs.create(dvs_name=dvs_external, private_vlan=False)
    # Connect all esxi hosts to dvs
    dvs.add_hosts(hosts_list=host_list, dvs_name=dvs_external, attach_uplink=True)
    # Add port group to dvs
    dvpg.create(dv_pg_name=dvpg_external, dvs_name=dvs_external, vlan_type='trunk', vlan_list=[0, 4094])

    # Create Distributed Switch for internal vmware traffic
    dvs.create(dvs_name=dvs_internal, private_vlan=True)
    # Connect all esxi hosts to dvs
    dvs.add_hosts(hosts_list=host_list, dvs_name=dvs_internal, attach_uplink=False)
    # Add port group to dvs
    dvpg.create(dv_pg_name=dvpg_internal, dvs_name=dvs_internal, vlan_type='trunk', vlan_list=[0, 4094])

    # Specify disk for contrail vm
    vm.add_disk(vm_disk_size)
    # Specify network adapter for contrail vm
    vm.add_nic(dv_pg_name=dvpg_external)
    vm.add_nic(dv_pg_name=dvpg_internal)
    # Create contrail vm on all hosts in datacenter
    for h in hosts:
        vm_name = 'ContrailVM-' + h
        vm.create(name=vm_name, cpu=vm_cpu, memory=vm_memory, storage_name=storage_name, host=h)
        vm.power_on(vm_name)

