#!/usr/bin/env python

import os
import sys
import argparse
import atexit
import yaml
import errno

from pyVmomi import vmodl
from pyVmomi import vim

from pyVim import connect
from fuelclient.objects import Environment
from fuelclient import fuelclient_settings


class Fuel(object):
    def __init__(self):
        self.settings = fuelclient_settings.get_settings()
        self._environment = None
        self._data = None
        self._fuel_attributes = None
        self.options = self.get_options()
        self._plugin_data = None

    def debug(self, *args):
        if self.options.verbose:
            sys.stderr.write(' '.join(args) + "\n")

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

    @staticmethod
    def get_options():
        """
        Parse the CLI options
        :return:
        """
        parser = argparse.ArgumentParser()

        parser.add_argument('-e', '--env',
                            required=True,
                            action='store',
                            help='The Fuel environment number to get settings from')

        parser.add_argument('-y', '--yaml',
                            required=False,
                            action='store_true',
                            help='Yaml format output')

        parser.add_argument('-v', '--verbose',
                            required=False,
                            action='store_true',
                            help='Verbose output for debugging')

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
        """
        :return:
        :rtype: dict
        """
        if self._fuel_attributes:
            return self._fuel_attributes
        attributes = self.environment.get_vmware_settings_data()

        try:
            attributes = attributes['editable']['value']['availability_zones'][0]
        except StandardError:
            print('Could not parse vmware data from API')
            raise
        self._fuel_attributes = attributes
        return self._fuel_attributes

    @property
    def plugin_data(self):
        """
        The plugin settings structure for the provided plugin version.
        Or the first one if there is no version provided.
        :rtype: dict
        """
        if self._plugin_data:
            return self._plugin_data
        latest_plugin_data = None
        latest_plugin_version = None
        for plugin_data in self.versions_data:
            plugin_version = map(int, str(plugin_data['metadata']['plugin_version']).split('.'))
            if plugin_version > latest_plugin_version:
                latest_plugin_version = plugin_version
                latest_plugin_data = plugin_data
        self._plugin_data = latest_plugin_data
        return self._plugin_data

    @property
    def plugin_settings(self):
        plugin_settings = {
            'private_vswitch_pg': self.plugin_data['private_vswitch_pg']['value'],
            'vcenter_dvswitch': self.plugin_data['contrail_vcenter_dvswitch']['value'],
            'vcenter_dvswitch_pg': self.plugin_data['contrail_vcenter_dvportgroup']['value'],
        }
        return plugin_settings


###########################################################


class Vcenter(object):
    def __init__(self):
        self._connect_to_vcenter = None
        self.fuel = Fuel()
        self._hosts_port_groups = None
        self._content = None
        self._vms = None
        self.fuel_attributes = self.fuel.fuel_attributes
        self.hosts = self.get_hosts
    @property
    def connect_to_vcenter(self):
        """
        :return:
        """
        if self._connect_to_vcenter:
            return self._connect_to_vcenter
        try:
            vcenter_settings = {
                'vcenter_ip':       self.fuel_attributes['vcenter_host'],
                'vcenter_password': self.fuel_attributes['vcenter_password'],
                'vcenter_user':     self.fuel_attributes['vcenter_username'],
            }
            service_instance = connect.SmartConnect(
                host=vcenter_settings['vcenter_ip'],
                user=vcenter_settings['vcenter_user'],
                pwd= vcenter_settings['vcenter_password'],
                port=443,
            )
            atexit.register(connect.Disconnect, service_instance)
        except vmodl.MethodFault as error:
            print("Caught vmodl fault : " + error.msg)
            raise

        self._connect_to_vcenter = service_instance
        return self._connect_to_vcenter

    @property
    def get_hosts(self):
        """
        :return: List of found ESXi hosts
        :rtype: list
        """
        host_view = self.content.viewManager.CreateContainerView(
            self.content.rootFolder,
            [vim.HostSystem],
            True,
        )
        hosts = [host for host in host_view.view]
        host_view.Destroy()
        return hosts

    def get_vm_nics(self, vm):
        """
        Receive the list of network interfaces for this ESXi vm
        :param vm:
        :return:
        :rtype: list
        """
        nic_list = []
        for dev in vm.config.hardware.device:
            if isinstance(dev, vim.vm.device.VirtualEthernetCard):
                dev_backing = dev.backing
                vlan_id = None
                v_switch = None
                if hasattr(dev_backing, 'port'):
                    port_group_key = dev.backing.port.portgroupKey
                    dvs_uuid = dev.backing.port.switchUuid
                    try:
                        dvs = self.content.dvSwitchManager.QueryDvsByUuid(dvs_uuid)
                    except StandardError:
                        port_group = "** Error: DVS not found **"
                        vlan_id = "NA"
                        v_switch = "NA"
                    else:
                        pg_obj = dvs.LookupDvPortGroup(port_group_key)
                        port_group = pg_obj.config.name
                        v_switch = str(dvs.name)
                else:
                    port_group = dev.backing.network.name
                    vm_host = vm.runtime.host
                    # global variable hosts is a list, not a dict
                    host_pos = self.hosts.index(vm_host)
                    view_host = self.hosts[host_pos]
                    # global variable host_pg_dict stores portgroups per host
                    pgs = self.hosts_port_groups[view_host]
                    for pg in pgs:
                        if port_group in pg.key:
                            vlan_id = str(pg.spec.vlanId)
                            v_switch = str(pg.spec.vswitchName)
                if port_group is None:
                    port_group = 'NA'
                if vlan_id is None:
                    vlan_id = 'NA'
                if v_switch is None:
                    v_switch = 'NA'
                self.fuel.debug('\t' + dev.deviceInfo.label + '->' + dev.macAddress +
                      ' @ ' + v_switch + '->' + port_group +
                      ' (vlan ' + vlan_id + ')')
                nic = {
                    'niclabel': dev.deviceInfo.label,
                    'macAddress': dev.macAddress,
                    'vSwitch': v_switch,
                    'portGroup': port_group,
                    'vlanId': vlan_id,
                }
                nic_list.append(nic)
        return nic_list

    @property
    def content(self):
        """
        :return:
        """
        if self._content:
            return self._content
        self._content = self.connect_to_vcenter.RetrieveContent()
        return self._content

    @property
    def hosts_port_groups(self):
        """
        :return: A dict of hosts and their port groups
        :rtype: dict
        """
        if self._hosts_port_groups:
            return self._hosts_port_groups
        self._hosts_port_groups = {}
        for host in self.hosts:
            pgs = host.config.network.portgroup
            self._hosts_port_groups[host] = pgs
        return self._hosts_port_groups

    @property
    def vms(self):
        """
        :return:
        :rtype: list
        """
        if self._vms:
            return self._vms
        vm_view = self.content.viewManager.CreateContainerView(
            self.content.rootFolder,
            [vim.VirtualMachine],
            True,
        )
        self._vms = [vm for vm in vm_view.view]
        vm_view.Destroy()
        return self._vms

    def print_vm_info(self, vm):
        """
        Collect the VM's name and the list of nics
        :param vm:
        :return:
        :rtype: dict
        """
        nics = self.get_vm_nics(vm)
        vminfo = {
            'vmName': vm.name,
            'nics': nics,
        }
        return vminfo

    @property
    def hosts_all_data(self):
        """
        :return:
        :rtype: list
        """
        host_list = []
        for host_id in self.hosts_port_groups:
            entry = {
                host_id.name: []
            }
            for vm in self.vms:
                vcenter_vm_info = self.print_vm_info(vm)
                n_name = vcenter_vm_info['vmName']
                entry[host_id.name].append({n_name: vcenter_vm_info['nics']})
            host_list.append(entry)
        return host_list

    def main(self):
        vcenter_dvswitch = self.fuel.plugin_settings['vcenter_dvswitch']
        vcenter_dvswitch_pg = self.fuel.plugin_settings['vcenter_dvswitch_pg']
        contrail_vm_data = {}
        contrail_vm_list = []
        for data in self.hosts_all_data:
            for host, vms in data.iteritems():
                self.fuel.debug('The vms information for host', host, '\n',  yaml.dump(vms))
                for vm in vms:
                    self.fuel.debug(yaml.dump(vm))
                    for vm_name, interfaces_list in vm.iteritems():
                        self.fuel.debug('The interface config for vm: ', vm_name, '\n', yaml.dump(interfaces_list))
                        for interface in interfaces_list:
                            self.fuel.debug('Interface configuration', yaml.dump(interface))
                            if interface['vSwitch'] == vcenter_dvswitch and \
                                    interface['portGroup'] == vcenter_dvswitch_pg:
                                contrail_vm_list.append(interface['macAddress'])
                                contrail_vm_data[host] = contrail_vm_list
        host_to_mac_binding = contrail_vm_data

        if self.fuel.options.yaml:
            path = '/var/lib/fuel/contrail/'
            try:
                os.makedirs(path)
            except OSError as exc:
                if exc.errno == errno.EEXIST and os.path.isdir(path):
                    pass
                else:
                    raise

            file_path = path + '{CLUSTER}_host_to_mac_bind.yaml'
            with open(file_path.format(CLUSTER=self.fuel.options.env), 'w') as outfile:
                outfile.write(yaml.dump(host_to_mac_binding, explicit_start=True, default_flow_style=False))
        else:
            print(yaml.dump(host_to_mac_binding, explicit_start=True, default_flow_style=False))

###########################################################

if __name__ == '__main__':
    vcenter = Vcenter()
    vcenter.main()
