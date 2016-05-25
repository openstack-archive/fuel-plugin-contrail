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

import subprocess
from fuelweb_test import logger
from devops.helpers.helpers import wait
from proboscis.asserts import assert_true


from . import settings


class BMDriver(object):
    """Manage Baremetal environment"""

    def __init__(self):
        self.conf = settings.BAREMETAL

    def bm_reboot(self):
        """Reboot slave host via IPMI"""

        ipmi_host = self.conf['ipmi_host']
        ipmi_user = self.conf['ipmi_user']
        ipmi_password = self.conf['ipmi_password']

        ipmi_cmd = ['/usr/bin/ipmitool',
                    '-H', ipmi_host,
                    '-U', ipmi_user,
                    '-P', ipmi_password,
                    'power', 'cycle']
        logger.info('Reboot node via IPMI')
        output = subprocess.check_output(ipmi_cmd)
        logger.debug('Reboot server output: {0}'.format(output))
        return True

    def setup_host_nets(self):
        """Setup master host - add necessary bridge interfaces"""
        bm_cfg = self.conf['host_bridge_interfaces']
        logger.info('Setup BM node interfaces "{0}"'.format(bm_cfg))
        ports = []
        for cfg in bm_cfg.replace(' ', '').split(';'):
            if cfg:
                ports.append(cfg.split(':'))
        for br in ports:
            logger.info('Add iface "{0}" as a port of the bridge "{1}"'.format(
                *br))
            ret = subprocess.call('sudo brctl addif {0} {1}'.format(*br),
                                  shell=True)
            logger.debug('Add iface result: {0}'.format(ret))

    def wait4node_status(self, obj, node_mac, status='discover',
                         timeout=settings.DEPLOY_CLUSTER_TIMEOUT):
        """Wait until slave host is ready"""

        logger.info('Wait for node "{0}" status "{0}"'.format(node_mac,
                                                              status))

        def check_func():
            node = self.get_bm_node(obj, node_mac)
            if node['status'] == status:
                logger.info('Node found,'
                            ' id:{id},'
                            ' status:{status},'
                            ' name:{name},'
                            ' cluster:{cluster}'.format(**node))
                return True
            else:
                logger.warning("Node found, but has unexpected status."
                               ' id:{id},'
                               ' status:{status},'
                               ' name:{name},'
                               ' cluster:{cluster}.'
                               ' wait...'.format(**node))
                return False
        wtime = wait(check_func, interval=30, timeout=timeout)
        logger.info('Node up in {0} sec.'.format(wtime))

    def get_bm_node(self, obj, node_mac):
        """Search for nailgun node by it's MAC address"""
        for node in obj.fuel_web.client.list_nodes():
            if node['mac'] == node_mac:
                return node
        return None

    def setup_fuel_node(self, obj, cluster_id, roles,
                        pending_addition=True, pending_deletion=False,
                        update_nodegroups=False, update_interfaces=True):
        """Setup roles for nailgun node"""

        node = self.get_bm_node(obj, self.conf['target_mac'])
        logger.info('Setup node "{0}" roles: "{1}"'.format(node['name'],
                                                           roles))
        # update nodes in cluster
        nodes_data = []
        nodes_groups = {}
        updated_nodes = []

        node_group = 'default'

        assert_true(node['online'],
                    'Node {0} is offline'.format(node['mac']))

        name = 'Node_{0}_{1}'.format(self.conf['target_mac'],
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
            self.update_node_interfaces(obj, node)
            self.update_networks(obj)
        if update_nodegroups:
            obj.fuel_web.update_nodegroups(cluster_id=cluster_id,
                                           node_groups=nodes_groups)

        return nailgun_nodes

    def update_node_interfaces(self, obj, node):
        """Update network interfacess for nailgun node"""

        conf_nets = self.conf['host_fuel_interfaces']
        networks = {}
        for interfaces in conf_nets.replace(' ', '').split(';'):
            logger.info('interfaces: {0}'.format(interfaces))
            if interfaces:
                interface, roles = interfaces.split(':')
                networks[interface] = roles.split(',')

        logger.info('Assigned BM networks are: {}'.format(
            str(networks)))
        obj.fuel_web.update_node_networks(node['id'], networks)

    def update_networks(self, obj):
        """Configure private network (disable vlan and etc.)"""

        nets = obj.fuel_web.client.get_networks(obj.cluster_id)
        nets['networking_parameters']['floating_ranges'][0] = [
            "10.109.1.130",
            "10.109.1.254"
        ]
        for net in nets['networks']:
            if net['name'] == 'public':
                net['ip_ranges'][0] = ['10.109.1.2', '10.109.1.127']
                net['cidr'] = '10.109.1.0/24'
                net['gateway'] = '10.109.1.1'
            elif net['name'] == 'storage':
                net['ip_ranges'][0] = ['10.109.4.2', '10.109.4.127']
                net['cidr'] = '10.109.4.0/24'
            elif net['name'] == 'management':
                net['ip_ranges'][0] = ['10.109.2.2', '10.109.2.127']
                net['cidr'] = '10.109.2.0/24'
            elif net['name'] == 'private':
                net['ip_ranges'][0] = ['10.109.3.2', '10.109.3.127']
                net['cidr'] = '10.109.3.0/24'
            net['vlan_start'] = None
            net['meta']['notation'] = 'ip_ranges'

        obj.fuel_web.client.update_network(
            obj.cluster_id,
            networking_parameters=nets['networking_parameters'],
            networks=nets['networks'])

    def host_prepare(self, obj):
        """Prepare slave host for deploy"""
        self.setup_host_nets()
        self.bm_reboot()

        node_mac = self.conf['target_mac']
        self.wait4node_status(obj, node_mac, status='discover')

