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


class Fuel(object):
    def debug(self, *args):
        sys.stderr.write(' '.join(args) + "\n")

    def __init__(self):
        self.settings = fuelclient_settings.get_settings()
        self._vcenter_settings = None
        self._environment = None
        self._data = None
        self._fuel_attributes = None
        self.options = self.get_options()

    @property
    def data(self):
        """
        The settings data returned by the Fuel client
        :rtype: dict
        """
        if self._data:
            return self._data
        self._data = self.environment.get_settings_data()
        if not isinstance(self._data, dict):
            raise RuntimeError('Could not get the cluster settings data!')
        return self._data

    def get_options(self):

        parser = argparse.ArgumentParser()

        parser.add_argument('-e', '--env',
                            required=True,
                            action='store',
                            help='The Fuel environment number to get settings from')

        parser.add_argument('-y', '--yaml',
                            required=False,
                            action='store_true',
                            help='Yaml format output')

        got_options = parser.parse_args()
        return got_options

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

    @property
    def environment(self):
        """
        The instance of the Fuel Client for this cluster
        :rtype: fuelclient.objects.environment.Environment
        """
        if self._environment:
            return self._environment
        self._environment = Environment(self.options.env)
        return self._environment

    @property
    def fuel_attributes(self):
        if self._fuel_attributes:
            return self._fuel_attributes

        attrs_json = self.environment.get_vmware_settings_data()

        try:
            attrs_json = attrs_json['editable']['value']['availability_zones'][0]
        except StandardError:
            self.debug('Could not parse vmware data from API')
            raise
        self._fuel_attributes = attrs_json
        return self._fuel_attributes

    @property
    def vcenter_settings(self):
        """
        The VCenter settings for provided environment
        :rtype: dict
        """
        vc_data = {
            'vcenter_ip': self.fuel_attributes['vcenter_host'],
            'vcenter_password': self.fuel_attributes['vcenter_password'],
            'vcenter_user': self.fuel_attributes['vcenter_username'],
        }
        return vc_data

    @property
    def plugin_data(self):
        """
        The plugin settings structure for the provided plugin version.
        Or the first one if there is no version provided.
        :rtype: dict
        """

        latest_plugin_data = None
        latest_plugin_version = None
        for plugin_data in self.versions_data:
            plugin_version = map(int, str(plugin_data['metadata']['plugin_version']).split('.'))
            if plugin_version > latest_plugin_version:
                latest_plugin_version = plugin_version
                latest_plugin_data = plugin_data

        return latest_plugin_data

    @property
    def plugin_settings(self):

        plugin_settings = {
            'private_vswitch_pg': self.plugin_data['private_vswitch_pg']['value'],
            'vcenter_dvswitch': self.plugin_data['contrail_vcenter_dvswitch']['value'],
            'vcenter_dvswitch_pg': self.plugin_data['contrail_vcenter_dvportgroup']['value'],
        }
        return plugin_settings


class Vcenter(object):
    def __init__(self):
        self._connect_to_vcenter = None
        self.fuel = Fuel()
        self._get_hosts_portgroups = None
        self._content = None

    def debug(self, *args):
        sys.stderr.write(' '.join(args) + "\n")

    @property
    def connect_to_vcenter(self):
        if self._connect_to_vcenter:
            return self._connect_to_vcenter
        try:
            service_instance = connect.SmartConnect(
                host=self.fuel.vcenter_settings['vcenter_ip'],
                user=self.fuel.vcenter_settings['vcenter_user'],
                pwd=self.fuel.vcenter_settings['vcenter_password'],
                port=443, )

            # datacenter = self.content.rootFolder.childEntity[0]
            # network_folder = datacenter.networkFolder
            atexit.register(connect.Disconnect, service_instance)
        except vmodl.MethodFault as error:
            print("Caught vmodl fault : " + error.msg)
            return -1

        self._connect_to_vcenter = service_instance
        return self._connect_to_vcenter

    def get_vm_hosts(self, content):
        # print("Getting all ESX hosts ...")
        host_view = content.viewManager.CreateContainerView(
            content.rootFolder,
            [vim.HostSystem],
            True,
        )
        obj = [host for host in host_view.view]
        host_view.Destroy()
        return obj

    def get_vm_nics(self, vm):
        niclist = []
        for dev in vm.config.hardware.device:
            if isinstance(dev, vim.vm.device.VirtualEthernetCard):
                dev_backing = dev.backing
                port_group = None
                vlan_id = None
                v_switch = None
                if hasattr(dev_backing, 'port'):
                    portGroupKey = dev.backing.port.portgroupKey
                    dvsUuid = dev.backing.port.switchUuid
                    try:
                        dvs = self.content.dvSwitchManager.QueryDvsByUuid(dvsUuid)
                    except:
                        port_group = "** Error: DVS not found **"
                        vlan_id = "NA"
                        v_switch = "NA"
                    else:
                        pg_obj = dvs.LookupDvPortGroup(portGroupKey)
                        port_group = pg_obj.config.name
                        # vlan_id = str(pgObj.config.defaultPortConfig.vlan.vlanId)
                        v_switch = str(dvs.name)
                else:
                    port_group = dev.backing.network.name
                    vm_host = vm.runtime.host
                    # global variable hosts is a list, not a dict
                    host_pos = self.hosts.index(vm_host)
                    view_host = self.hosts[host_pos]
                    # global variable host_pg_dict stores portgroups per host
                    host_pg_dict = self.get_hosts_portgroups(self.hosts)
                    pgs = host_pg_dict[view_host]
                    for p in pgs:
                        if port_group in p.key:
                            vlan_id = str(p.spec.vlanId)
                            v_switch = str(p.spec.vswitchName)
                if port_group is None:
                    port_group = 'NA'
                if vlan_id is None:
                    vlan_id = 'NA'
                if v_switch is None:
                    v_switch = 'NA'
                # print('\t' + dev.deviceInfo.label + '->' + dev.macAddress +
                #      ' @ ' + vSwitch + '->' + portGroup +
                #      ' (VLAN ' + vlanId + ')')
                nic = {
                    'niclabel': dev.deviceInfo.label,
                    'macAddress': dev.macAddress,
                    'vSwitch': v_switch,
                    'portGroup': port_group,
                    'vlanId': vlan_id,
                }
                niclist.append(nic)
        # print(niclist)
        return niclist

    @property
    def content(self):
        if self._content:
            return self._content
        self._content = self.connect_to_vcenter.RetrieveContent()
        return self.connect_to_vcenter.RetrieveContent()

    @property
    def hosts(self):
        return self.get_vm_hosts(self.content)

    def get_hosts_portgroups(self, hosts):
        # print("Collecting portgroups on all hosts. This may take a while ...")
        if self._get_hosts_portgroups:
            return self._get_hosts_portgroups
        hostPgDict = {}
        for host in hosts:
            pgs = host.config.network.portgroup
            hostPgDict[host] = pgs
            # print("\tHost {} done.".format(host.name))
        # print("\tPortgroup collection complete.")
        self._get_hosts_portgroups = hostPgDict
        return hostPgDict

    @staticmethod
    def get_vms(content):
        # print("Getting all VMs ...")
        vm_view = content.viewManager.CreateContainerView(content.rootFolder,
                                                          [vim.VirtualMachine],
                                                          True)
        obj = [vm for vm in vm_view.view]
        vm_view.Destroy()
        return obj

    def print_vm_info(self, vm):
        # vm_power_state = vm.runtime.powerState
        # print("Found VM:", vm.name + "(" + vmPowerState + ")")
        nics = self.get_vm_nics(vm)
        vminfo = {
            'vmName': vm.name,
            # 'vmState': str(vm_power_state),
            'nics': nics,
        }
        return vminfo

    @property
    def get_all_data(self):
        hostlist = []
        vms = self.get_vms(self.content)
        host_pg_dict = self.get_hosts_portgroups(self.hosts)
        for host_id in host_pg_dict:
            entry = {host_id.name: []}
            for vm in vms:
                vcenter_vminfo = self.print_vm_info(vm)
                n_name = vcenter_vminfo['vmName']
                entry[host_id.name].append({n_name: vcenter_vminfo['nics']})
            hostlist.append(entry)
        return hostlist

    def main(self):
        all_data = self.get_all_data
        # print(yaml.dump(all_data))
        vcenter_dvswitch = self.fuel.plugin_settings['vcenter_dvswitch']
        vcenter_dvswitch_pg = self.fuel.plugin_settings['vcenter_dvswitch_pg']
        contrail_vm_data = {}
        contrail_vm_list = []
        for data in all_data:
            for host, vms in data.iteritems():
                # print 'The vms information for host', host, '\n',  yaml.dump(vms)
                for vm in vms:
                    # print(yaml.dump(vm))
                    for vmname, interfaces_list in vm.iteritems():
                        # print 'The interface config for vm: ', vmname, '\n', yaml.dump(interfaces_list)
                        for interface in interfaces_list:
                            # print 'Interface configuration', yaml.dump(interface)
                            if interface['vSwitch'] == vcenter_dvswitch and \
                                            interface['portGroup'] == vcenter_dvswitch_pg:
                                contrail_vm_list.append(interface['macAddress'])
                                contrail_vm_data[host] = contrail_vm_list
            host_to_mac_binding = contrail_vm_data

        if self.fuel.options.yaml:
            path = '/var/lib/fuel/contrail/'
            try:
                os.makedirs(path)
            except OSError:
                if os.path.exists(path):
                    pass
                else:
                    raise

            filepath = path + '{CLUSTER}_host_to_mac_bind.yaml'
            with open(filepath.format(CLUSTER=self.fuel.options.env), 'w') as outfile:
                outfile.write(yaml.dump(host_to_mac_binding, explicit_start=True, default_flow_style=False))
        else:
            print(yaml.dump(host_to_mac_binding, explicit_start=True, default_flow_style=False))


if __name__ == '__main__':
    vcenter = Vcenter()
    vcenter.main()
