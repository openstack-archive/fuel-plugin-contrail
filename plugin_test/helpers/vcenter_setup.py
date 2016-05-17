import os
import libvirt
import subprocess
import brctl
import ip
import vmrun


from fuelweb_test import logger
from fuelweb_test.settings import ENV_NAME

from proboscis.asserts import assert_true


class Vcenter(object):

    def __init__(self):
        super(Vcenter, self).__init__()

    libvirt_con = libvirt.open("qemu:///system")
    bridge = brctl.BridgeCTL()
    ip = ip.IP()

    host_type = 'ws-shared'
    path_to_vmx_file = '"[standard] {0}/{0}.vmx"'
    host_name = 'https://localhost:443/sdk'
    WORKSTATION_NODES = os.environ.get('WORKSTATION_NODES').split(' ')
    WORKSTATION_USERNAME = os.environ.get('WORKSTATION_USERNAME')
    WORKSTATION_PASSWORD = os.environ.get('WORKSTATION_PASSWORD')
    VCENTER_IP = os.environ.get('VCENTER_IP')
    WORKSTATION_IFS = os.environ.get('WORKSTATION_IFS').split(' ')
    WORKSTATION_SNAPSHOT = os.environ.get('WORKSTATION_SNAPSHOT')
    vcenter_nic = [
        {'net':'{0}_public'.format(ENV_NAME),
         'nic':WORKSTATION_IFS[0], 'ip':'172.16.0.1/24'},
        {'net':'{0}_private'.format(ENV_NAME),
         'nic':WORKSTATION_IFS[1], 'ip':'10.0.0.1/24'}]

    def _add_nic_to_bridge(self, nics):
        bridges = []
        for interface_param in nics:
            bridge_name = self.libvirt_con.networkLookupByName(
                interface_param['net']).bridgeName()

            logger.info('Add nic {0} to bridge {1}.'.format(
                interface_param['nic'], bridge_name))
            self.bridge.stp(bridge_name, 'off')
            self.bridge.add_interface(bridge_name, interface_param['nic'])

            logger.info('Enable link on bridge {0}.'.format(bridge_name))
            self.ip.set_link(bridge_name)

            logger.info(
                'Remove {0} ifre it is assighned to any bridges.'.format(
                    interface_param['ip']))
            self._remove_ip_from_bridge(interface_param['ip'])
            logger.info(
                'Add {0} to  bridge {1}.'.format(
                    interface_param['ip'], bridge_name))
            self.ip.add_ip_address(bridge_name, interface_param['ip'])

            """
            command = 'sudo /sbin/iptables-save |grep {0} | grep'.format(
                bridge_name) + \
            ' -i reject| grep -q FORWARD'
            iptables = subprocess.call(command, shell=True)
            if iptables == '':
                command = 'sudo /sbin/iptables -D FORWARD' + \
                ' -o {} -j REJECT --reject-with icmp-port-unreachable'.format(
                    bridge_name)
                subprocess.call(command, shell=True)
                command = 'sudo /sbin/iptables -D FORWARD' + \
                ' -i {} -j REJECT --reject-with icmp-port-unreachable'.format(
                    bridge_name)
                subprocess.call(command, shell=True)
              """
            bridges.append(bridge_name)

        return bridges

    def _clean_old_nics(self, nics):
        networks = self.libvirt_con.listNetworks()
        for interface_param in nics:
            net_name = [
                net for net in networks
                if interface_param['net'] in net].pop()
            bridge_name = self.libvirt_con.networkLookupByName(
                net_name).bridgeName()
            if bridge_name:
                bridge_interfaces = self.bridge.get_interfaces_list(bridge_name)
                if interface_param['nic'] in bridge_interfaces:
                    self.bridge.delete_interface(
                        bridge_name, interface_param['nic'])
                    self.ip.set_link(bridge_name, state='down')

    def _clean_ip_tables(self):
        commands = [
            'sudo /sbin/iptables -F',
            'sudo /sbin/iptables -t nat -F',
            'sudo /sbin/iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE']

        for cmd in commands:
            subprocess.call(cmd, shell=True)

    def _remove_ip_from_bridge(self, ip):
        bridge_names = self.ip.get_interface_by_ip(ip)
        for br in bridge_names:
            self.ip.delete_ip_address(br, ip)

    def setup(self):
        self._clean_old_nics(self.vcenter_nic)
        self._add_nic_to_bridge(self.vcenter_nic)
        self._clean_ip_tables()

        for node_name in self.WORKSTATION_NODES:
            logger.info("Revert {0} node to snpashot {1}".format(
                node_name, self.WORKSTATION_SNAPSHOT))
            node = vmrun.Vmrun(
                self.host_type,
                self.path_to_vmx_file.format(node_name),
                host_name=self.host_name,
                username=self.WORKSTATION_USERNAME,
                password=self.WORKSTATION_PASSWORD)
            node.revert_to_snapshot(self.WORKSTATION_SNAPSHOT)
            node.start()
