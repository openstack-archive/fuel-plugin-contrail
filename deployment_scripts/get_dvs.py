#!/usr/bin/env python

import os
import sys
import argparse
import atexit
import yaml

from pyVmomi import vmodl
from pyVmomi import vim

from pyVim import connect
from fuelclient.objects import Environment
from fuelclient import fuelclient_settings


class fuel(object):
    _options = None
    _vcenter_settings = None
    _client = None
    _plugin_data = None
    _data = None
    _plugin_settings = None
    _fuel_connection = None

    def debug(self, *args):
        sys.stderr.write(' '.join(args) + "\n")

    def __init__(self):
        self._plugin_version = self.options.ver
        self.settings = fuelclient_settings.get_settings()

    @property
    def data(self):
        """
        The settings data returned by the Fuel client
        :rtype: dict
        """
        if self._data:
            return self._data
        self._data = self.client.get_settings_data()
        if not isinstance(self._data, dict):
            raise RuntimeError('Could not get the cluster settings data!')
        return self._data

    @property
    def options(self):
        if self._options:
            return self._options

        parser = argparse.ArgumentParser()

        parser.add_argument('-e', '--env',
                            required=True,
                            action='store',
                            help='The Fuel environment number to get settings from')

        parser.add_argument('-v', '--ver',
                            required=False,
                            action='store',
                            default=0,
                            help='The Contrail-plugin version to get settings from')

        parser.add_argument('-y', '--yaml',
                            required=False,
                            action='store_true',
                            default=False,
                            help='Yaml format output')

        parser.set_defaults(yaml=False)

        self._options = parser.parse_args()
        return self._options

    @property
    def plugin_version(self):
        """
        The plugin version. Optional.
        :rtype: str, None
        """
        if self._plugin_version:
            return self._plugin_version
        if len(str(self.options.ver)) >= 3:
            return str(self.options.ver)
        else:
            return None

    @property
    def versions_data(self):
        """
        The "versions" structure inside the settings data.
        It contains a list of Contrail plugin data structures
        for every version of the plugin.
        :rtype: list
        """
        versions = self.data.get('editable', {}).get('contrail', {}).get('metadata', {}).get('versions', [])
        if not isinstance(versions, list) or len(versions) == 0:
            raise RuntimeError('Could not find the contrail versions data block!')
        return versions

    def ver_compare(self, a, b):
        a1, a2, a3 = a.split('.')
        b1, b2, b3 = b.split('.')
        if int(a1) - int(b1) <> 0:
            return int(b1) - int(a1)
        if int(a2) - int(b2) <> 0:
            return int(b2) - int(a2)
        if int(a3) - int(b3) <> 0:
            return int(b3) - int(a3)
        return 0

    @property
    def client(self):
        """
        The instance of the Fuel Client for this cluster
        :rtype: fuelclient.objects.environment.Environment
        """
        if self._client:
            return self._client
        self._client = Environment(self.options.env)
        return self._client

    @property
    def fuel_connection(self):
        if self._fuel_connection:
            return self._fuel_connection

        env = Environment(self.options.env)
        attrs_json = env.get_vmware_settings_data()

        try:
            attrs_json = attrs_json['editable']['value']['availability_zones'][0]
        except:
            self.debug('Could not parse vmware data from API')
        self._fuel_connection = attrs_json
        return self._fuel_connection

    @property
    def vcenter_settings(self):
        """
        The VCenter settings for provided environment
        :rtype: list of dicts
        """
        if self._vcenter_settings:
            return self._vcenter_setings

        vc_data = {
             'vcenter_ip': self.fuel_connection['vcenter_host'],
             'vcenter_password': self.fuel_connection['vcenter_password'],
             'vcenter_user': self.fuel_connection['vcenter_username'],
        }
        self._vcenter_setings = vc_data
        return self._vcenter_setings

    @property
    def plugin_data(self):
        """
        The plugin settings structure for the provided plugin version.
        Or the first one if there is no version provided.
        :rtype: dict
        """
        if self._plugin_data:
            return self._plugin_data

        if not self.plugin_version:
            versions = []
            for version in self.versions_data:
                versions.append(str(version['metadata']['plugin_version']))
            self._plugin_version = sorted(versions, cmp=self.ver_compare)[0]
        for version in self.versions_data:
            if version.get('metadata', {}).get('plugin_version', None) == self.plugin_version:
                self._plugin_data = version
                break
        if not self._plugin_data:
            raise RuntimeError('Could not find any contrail data blocks for version: %s!' % self.plugin_version)
        return self._plugin_data

    @property
    def plugin_settings(self):
        """
        :return:
        """
        if self._plugin_settings:
            return self._plugin_settings
        self._plugin_settings = {
            #'private_switch'     : self.plugin_data['']['value'],
            'private_vswitch_pg' : self.plugin_data['private_vswitch_pg']['value'],
            'vcenter_dvswitch'   : self.plugin_data['contrail_vcenter_dvswitch']['value'],
            'vcenter_dvswitch_pg': self.plugin_data['contrail_vcenter_dvportgroup']['value'],
        }
        return self._plugin_settings

class vcenter(object):
    _connect_to_vcenter = None
    _options = fuel.options

    def debug(self, *args):
        sys.stderr.write(' '.join(args) + "\n")

    @property
    def connect_to_vcenter(self):
        if self._connect_to_vcenter:
            return self._connect_to_vcenter
        try:
            self.service_instance = connect.SmartConnect(
                host=fuel.vcenter_settings['vcenter_ip'],
                user=fuel.vcenter_settings['vcenter_user'],
                pwd=fuel.vcenter_settings['vcenter_password'],
                port=443,)

            self.content = self.service_instance.RetrieveContent()
            self.datacenter = self.content.rootFolder.childEntity[0]
            self.network_folder = self.datacenter.networkFolder
            atexit.register(connect.Disconnect, self.service_instance)
        except vmodl.MethodFault as error:
            print("Caught vmodl fault : " + error.msg)
            return -1

        self._connect_to_vcenter = self.service_instance
        return self._connect_to_vcenter


    @classmethod
    def GetVMHosts(self, content):
        #print("Getting all ESX hosts ...")
        host_view = content.viewManager.CreateContainerView(content.rootFolder,
                                                            [vim.HostSystem],
                                                            True)
        obj = [host for host in host_view.view]
        host_view.Destroy()
        return obj

    @classmethod
    def GetVMNics(self, vm):
        niclist = []
        for dev in vm.config.hardware.device:
            if isinstance(dev, vim.vm.device.VirtualEthernetCard):
                dev_backing = dev.backing
                portGroup = None
                vlanId = None
                vSwitch = None
                if hasattr(dev_backing, 'port'):
                    portGroupKey = dev.backing.port.portgroupKey
                    dvsUuid = dev.backing.port.switchUuid
                    try:
                        dvs = content.dvSwitchManager.QueryDvsByUuid(dvsUuid)
                    except:
                        portGroup = "** Error: DVS not found **"
                        vlanId = "NA"
                        vSwitch = "NA"
                    else:
                        pgObj = dvs.LookupDvPortGroup(portGroupKey)
                        portGroup = pgObj.config.name
                        #vlanId = str(pgObj.config.defaultPortConfig.vlan.vlanId)
                        vSwitch = str(dvs.name)
                else:
                    portGroup = dev.backing.network.name
                    vmHost = vm.runtime.host
                    # global variable hosts is a list, not a dict
                    host_pos = hosts.index(vmHost)
                    viewHost = hosts[host_pos]
                    # global variable hostPgDict stores portgroups per host
                    pgs = hostPgDict[viewHost]
                    for p in pgs:
                        if portGroup in p.key:
                            vlanId = str(p.spec.vlanId)
                            vSwitch = str(p.spec.vswitchName)
                if portGroup is None:
                    portGroup = 'NA'
                if vlanId is None:
                    vlanId = 'NA'
                if vSwitch is None:
                    vSwitch = 'NA'
                #print('\t' + dev.deviceInfo.label + '->' + dev.macAddress +
                #      ' @ ' + vSwitch + '->' + portGroup +
                #      ' (VLAN ' + vlanId + ')')
                nic = {
                    'niclabel'   : dev.deviceInfo.label,
                    'macAddress' : dev.macAddress,
                    'vSwitch'    : vSwitch,
                    'portGroup'  : portGroup,
                    'vlanId'     : vlanId,
                }
                niclist.append(nic)
        #print(niclist)
        return niclist

    @classmethod
    def GetVMHosts(self, content):
        #print("Getting all ESX hosts ...")
        host_view = content.viewManager.CreateContainerView(content.rootFolder,
                                                            [vim.HostSystem],
                                                            True)
        obj = [host for host in host_view.view]
        host_view.Destroy()
        return obj

    @classmethod
    def GetHostsPortgroups(self, hosts):
        #print("Collecting portgroups on all hosts. This may take a while ...")
        hostPgDict = {}
        for host in hosts:
            pgs = host.config.network.portgroup
            hostPgDict[host] = pgs
            #print("\tHost {} done.".format(host.name))
        #print("\tPortgroup collection complete.")
        return hostPgDict

    @classmethod
    def GetVMs(self, content):
        #print("Getting all VMs ...")
        vm_view = content.viewManager.CreateContainerView(content.rootFolder,
                                                          [vim.VirtualMachine],
                                                          True)
        obj = [vm for vm in vm_view.view]
        vm_view.Destroy()
        return obj

    @classmethod
    def PrintVmInfo(self, vm):
        vmPowerState = vm.runtime.powerState
        #print("Found VM:", vm.name + "(" + vmPowerState + ")")
        nics = self.GetVMNics(vm)
        vminfo = {
            'vmName' : vm.name,
            'vmState': str(vmPowerState),
            'nics'   : nics,
        }
        #print(vminfo)
        return vminfo

    @property
    def GetAllData(self):
        hostlist = []
        for host_id in hostPgDict:
            entry = {host_id.name: []}
            for vm in vms:
                vcenter_vminfo = vcenter.PrintVmInfo(vm)
                n_name = vcenter_vminfo['vmName']
                entry[host_id.name].append({n_name: vcenter_vminfo['nics']})
            hostlist.append(entry)
        return hostlist

if __name__ == '__main__':
    # -=-=- The work with fuel started here -=-=-
    fuel = fuel()
    #print(fuel.vcenter_settings)
    #print(fuel.plugin_settings)
    # -=-=- The work with fuel ended here -=-=-

    # -=-=- The work with vcenter started here -=-=-
    vcenter = vcenter()
    si = vcenter.connect_to_vcenter
    content = si.RetrieveContent()

    hosts = vcenter.GetVMHosts(content)

    hostPgDict = vcenter.GetHostsPortgroups(hosts)

    vms = vcenter.GetVMs(content)

    allData = vcenter.GetAllData

    #print(yaml.dump(allData))

    vcenter_dvswitch    = fuel.plugin_settings['vcenter_dvswitch']
    vcenter_dvswitch_pg = fuel.plugin_settings['vcenter_dvswitch_pg']
    contrail_vm_data = {}
    contrail_vm_list = []
    for data in allData:
        for host, vms in data.iteritems():
            #print 'The vms information for host', host, '\n',  yaml.dump(vms)
            for vm in vms:
                #print(yaml.dump(vm))
                for vmname, interfaces_list in vm.iteritems():
                    #print 'The interface config for vm: ', vmname, '\n', yaml.dump(interfaces_list)
                    for interface in interfaces_list:
                        #print 'Interface configuration', yaml.dump(interface)
                        if interface['vSwitch'] == vcenter_dvswitch and interface['portGroup'] == vcenter_dvswitch_pg:
                            contrail_vm_list.append(interface['macAddress'])
                            contrail_vm_data[host] = contrail_vm_list
        host_to_mac_binding = contrail_vm_data

    if fuel.options.yaml:
        path = '/var/lib/fuel/contrail/'
        try:
            os.makedirs(path)
        except OSError:
            if os.path.exists(path):
                pass
            else:
                raise

        filepath = path + '{CLUSTER}_host_to_mac_bind.yaml'
        with open(filepath.format(CLUSTER=fuel.options.env), 'w') as outfile:
            outfile.write(yaml.dump(host_to_mac_binding, explicit_start=True, default_flow_style=False))
    else:
        print(yaml.dump(host_to_mac_binding, explicit_start=True, default_flow_style=False))
    # -=-=- The work with vcenter ended here -=-=-
