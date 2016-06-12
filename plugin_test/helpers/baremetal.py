"""Copyright 2016 Mirantis, Inc.

Licensed under the Apache License, Version 2.0 (the "License"); you may
not use this file except in compliance with the License. You may obtain
a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
License for the specific language governing permissions and limitations
under the License.
"""

import time
import subprocess
from devops.helpers.helpers import wait
from fuelweb_test import logger
from fuelweb_test.settings import iface_alias
from proboscis.asserts import assert_true

from . import settings
from . import openstack


class BridgeTool(object):
    """Interface for bridge management."""

    @staticmethod
    def call_cmd(cmd):
        """Call wrapper for command."""
        try:
            res = subprocess.check_output(
                cmd,
                shell=True,
                stderr=subprocess.STDOUT).replace('\n', '')
        except subprocess.CalledProcessError as e:
            logger.error("Cmd ret code: {0}. Output: {1}".format(
                e.returncode, e.output))
            return e.output
        return res

    @staticmethod
    def get_bridge_name(netmask):
        """Return bridge name by it's netmask."""
        cmd = "ip route | grep '{0}' | awk '{{print $3}}'".format(netmask)
        res = BridgeTool.call_cmd(cmd)
        return res

    @staticmethod
    def check_bridge(bridge, interface):
        """Check interface in bridge."""
        cmd = "brctl show '{0}' | grep '{1}' | wc -l".format(
            bridge, interface)
        res = BridgeTool.call_cmd(cmd)
        if int(res) > 0:
            return True
        else:
            return False

    @staticmethod
    def del_interface(bridge, interface):
        """Delete interface from bridge."""
        cmd = "sudo brctl delif '{0}' '{1}'".format(bridge, interface)
        res = BridgeTool.call_cmd(cmd)
        return res

    @staticmethod
    def add_interface(bridge, interface):
        """Add interface from bridge."""
        cmd = "sudo brctl addif '{0}' '{1}'".format(bridge, interface)
        res = BridgeTool.call_cmd(cmd)
        return res


class BMDriver(object):
    """Manage Baremetal environment."""

    def __init__(self):
        """Init for this class."""
        self.conf = settings.BAREMETAL

    def bm_reboot(self):
        """Reboot slave host via IPMI."""
        ipmi_host = self.conf['ipmi_host']
        ipmi_user = self.conf['ipmi_user']
        ipmi_password = self.conf['ipmi_password']

        logger.info('Reboot node "{0}" via IPMI'.format(ipmi_host))
        ipmi_cmd = "/usr/bin/ipmitool" \
                   " -H {0}" \
                   " -U {1}" \
                   " -P {2}" \
                   " power cycle".format(ipmi_host, ipmi_user, ipmi_password)
        output = subprocess.check_output(ipmi_cmd, shell=True)
        logger.debug('Reboot server output: {0}'.format(output))
        time.sleep(10)
        return True

    def setup_host_nets(self):
        """Setup master host - add necessary bridge interfaces."""
        bm_cfg = self.conf['host_bridge_interfaces']

        logger.info('Setup BM node interfaces "{0}"'.format(bm_cfg))
        ports = []
        for cfg in bm_cfg.replace(' ', '').split(';'):
            if cfg:
                ports.append(cfg.split(':'))
        for br_interface in ports:
            bridge = BridgeTool.get_bridge_name(br_interface[1])
            if not bridge:
                raise Exception("Bridge not found for network: {0}".format(
                    br_interface[1]))
            if BridgeTool.check_bridge(bridge, br_interface[0]):
                logger.info('iface "{0}" already in bridge "{1}"'.format(
                    br_interface[0], bridge))
                continue
            logger.info('Add iface "{0}" as a port of the bridge "{1}"'.format(
                br_interface[0], bridge))
            ret = BridgeTool.add_interface(bridge, br_interface[0])
            logger.debug('Add iface result: {0}'.format(ret))

    def wait4node_status(self, obj, node_mac, status=['discover'],
                         timeout=settings.DEPLOY_CLUSTER_TIMEOUT):
        """Wait until slave host is ready."""
        logger.info('Wait for node "{0}" status "{1}"'.format(node_mac,
                                                              status))

        def check_func():
            node = self.get_bm_node(obj, node_mac)
            if not node:
                return False
            node_info = ('Info:'
                         ' id:{id},'
                         ' status:{status},'
                         ' name:{name},'
                         ' cluster:{cluster}.'.format(**node))
            if node['status'] in status:
                if not node['online']:
                    logger.info('Node found but "offline". ' +
                                node_info)
                    return False
                else:
                    logger.info('Node found. ' + node_info)
                    return True
            else:
                logger.warning("Node found, but has unexpected status. " +
                               node_info)
                return False
        wtime = wait(check_func, interval=30, timeout=timeout)
        logger.info('Node up in {0} sec.'.format(wtime))

    def get_bm_node(self, obj, node_mac):
        """Search for nailgun node by it's MAC address."""
        for node in obj.fuel_web.client.list_nodes():
            if node['mac'] in node_mac:
                return node
        return None

    def setup_fuel_node(self, obj, cluster_id, roles,
                        pending_addition=True, pending_deletion=False,
                        update_nodegroups=False, update_interfaces=True):
        """Setup roles for nailgun node."""
        node_mac = self.conf['target_macs']
        self.wait4node_status(obj, node_mac, status=['discover', 'ready'])

        node = self.get_bm_node(obj, node_mac)
        logger.info('Setup node "{0}" roles: "{1}"'.format(node['name'],
                                                           roles))
        # update nodes in cluster
        nodes_data = []
        nodes_groups = {}
        updated_nodes = []

        node_group = 'default'

        assert_true(node['online'],
                    'Node {0} is offline'.format(node['mac']))

        name = 'Node_{0}_{1}'.format(self.conf['target_macs'],
                                     "_".join(roles))

        logger.info('node at  name:{0}'.format(node['name']))
        logger.info('roles:{0}'.format(roles))
        logger.info('name:{0}'.format(name))

        node_data = {
            'cluster_id': cluster_id,
            'id': node['id'],
            'pending_addition': pending_addition,
            'pending_deletion': pending_deletion,
            'pending_roles': roles,
            'name': name
        }
        nodes_data.append(node_data)
        if node_group not in nodes_groups.keys():
            nodes_groups[node_group] = []
        nodes_groups[node_group].append(node)
        updated_nodes.append(node)

        # assume nodes are going to be updated for one cluster only
        cluster_id = nodes_data[-1]['cluster_id']
        node_ids = [str(node_info['id']) for node_info in nodes_data]

        obj.fuel_web.client.update_nodes(nodes_data)

        nailgun_nodes = obj.fuel_web.client.list_cluster_nodes(cluster_id)
        cluster_node_ids = map(lambda _node: str(_node['id']), nailgun_nodes)
        assert_true(
            all([node_id in cluster_node_ids for node_id in node_ids]))

        if update_interfaces and not pending_deletion:
            self.update_bm_node_interfaces(obj, node)
        if update_nodegroups:
            obj.fuel_web.update_nodegroups(cluster_id=cluster_id,
                                           node_groups=nodes_groups)

        return nailgun_nodes

    def update_bm_node_interfaces(self, obj, node):
        """Update network interfacess for nailgun node."""
        interfaces = self.get_node_interfaces(
            obj,
            node['id'],
            self.conf['target_macs'].split(';'))

        def get_free_interface(allocated=[]):
            ifaces = obj.fuel_web.client.get_node_interfaces(node['id'])
            for iface in ifaces:
                if iface['name'] not in allocated:
                    return iface['name']
            return None

        pxe_interface = interfaces['pxe']
        hw = interfaces['common']
        pub = get_free_interface([hw, pxe_interface])
        if pub is None:
            logger.warning("Interface for 'public' network not found.")
        else:
            logger.info("Assign 'public' net on '{0}'".format(pub))

        logger.info('Found PXE net: {0}; Slave net: {1}.'.format(
            pxe_interface, hw))

        networks = {
            pxe_interface: ['fuelweb_admin', 'storage', 'management'],
            hw: ['private'],
            pub: ['public']
        }

        logger.info('Assigned BM networks are: {}'.format(
            str(networks)))
        obj.fuel_web.update_node_networks(node['id'], networks)

    def update_vm_node_interfaces(self, obj, cluster_id):
        """Update network interfaces for node."""
        assigned_networks = {
            iface_alias('eth0'): ['fuelweb_admin', 'storage', 'management'],
            iface_alias('eth1'): ['public'],
            iface_alias('eth3'): ['private'],
        }
        logger.info('Assigned networks are: {}'.format(str(assigned_networks)))

        nailgun_nodes = obj.fuel_web.client.list_cluster_nodes(cluster_id)
        baremetal_macs = self.conf['target_macs']
        for node in nailgun_nodes:
            if node['mac'] in baremetal_macs:
                # Skip Barematal node
                continue
            obj.fuel_web.update_node_networks(node['id'], assigned_networks)

    def host_prepare(self):
        """Prepare slave host for deploy."""
        self.setup_host_nets()
        self.bm_reboot()

    def get_node_interfaces(self, obj, node_id, macs):
        """Return PXE and Common interfaces with given MACs for node.

        return:

            {'pxe': interface_name1, 'common': interface_name2}

        """
        interfaces = obj.fuel_web.client.get_node_interfaces(node_id)
        logger.info('Check node for PXE interfaces: {0}'.format(
            interfaces))
        iface_pxe = None
        iface_slave = None
        for iface in interfaces:
            logger.info("Check interface: {0}".format(iface))
            if iface['mac'] in macs:
                if iface['pxe']:
                    logger.info("Found PXE interface: {0}".format(iface))
                    iface_pxe = iface['name']
                else:
                    logger.info("Found slave interface: {0}".format(iface))
                    iface_slave = iface['name']
            if iface_pxe and iface_slave:
                logger.info('Found PXE net: {0}; Slave net: {1}.'.format(
                    iface_pxe, iface_slave
                ))
                return {'pxe': iface_pxe, 'common': iface_slave}
        return {'pxe': None, 'common': None}
