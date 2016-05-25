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
    def __init__(self):
        self.conf = settings.BAREMETAL

    def bm_reboot(self):
        ipmi_host = self.conf['ipmi_user']
        ipmi_user = self.conf['ipmi_user']
        ipmi_password = self.conf['ipmi_password']

        ipmi_cmd = ['/usr/bin/ipmitool', '-l', 'lan',
                    '-H', ipmi_host, '-U', ipmi_user, '-P', ipmi_password]
        logger.info('Reboot node via IPMI')
        cmd = ipmi_cmd + ['power', 'cycle']
        # output = subprocess.check_output(cmd)
        # logger.debug('Reboot server output: {0}'.format(output))
        return True

    def setup_nets(self):
        bm_cfg = self.conf['host_bridge_interfaces']
        logger.info('Setup BM node interfaces "{0}"'.format(bm_cfg))
        ports = []
        for cfg in bm_cfg.replace(' ', '').split(';'):
            ports.append(cfg.split(':'))
        for br in ports:
            logger.info('Add iface "{0}" as a port of the bridge "{1}"'.format(
                *br))
            # subprocess.call('sudo brctl addif {0} {1}'.format(*br), shell=True)

    def wait4node_status(self, obj, node_mac, status='discover',
                         timeout=settings.DEPLOY_CLUSTER_TIMEOUT):
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
        for node in obj.fuel_web.client.list_nodes():
            if node['mac'] == node_mac:
                return node
        return None

    def setup_fuel_node(self, obj, cluster_id, roles,
                        pending_addition=True, pending_deletion=False,
                        update_nodegroups=False, update_interfaces=True):
        node = self.get_bm_node(obj, self.conf['target_mac'])
        logger.info('Setup node "{0}" roles: "{1}"'.format(node['name'],
                                                           roles))
        # update nodes in cluster
        nodes_data = []
        nodes_groups = {}
        updated_nodes = []

        node_name = node['name']
        node_roles = roles
        node_group = 'default'

        assert_true(node['online'],
                    'Node {0} is offline'.format(node['mac']))

        name = '{0}_{1}'.format(node_name, "_".join(node_roles))

        node_data = {
            'cluster_id': cluster_id,
            'id': node['id'],
            'pending_addition': pending_addition,
            'pending_deletion': pending_deletion,
            'pending_roles': node_roles,
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
        if update_nodegroups:
            obj.fuel_web.update_nodegroups(cluster_id=cluster_id,
                                           node_groups=nodes_groups)

        return nailgun_nodes

    def update_node_interfaces(self, obj, node):
        conf_nets = self.conf['host_fuel_interfaces']
        networks = {}
        for interfaces in conf_nets.replace(' ','').split(';'):
            for interface, roles in interfaces.split(':'):
                networks[interface] = roles.split(',')

        logger.info('Assigned BM networks are: {}'.format(
            str(networks)))
        obj.fuel_web.update_node_networks(node['id'], networks)

    def host_prepare(self, obj):
        self.setup_nets()
        self.bm_reboot()

        node_mac = self.conf['target_mac']
        self.wait4node_status(obj, node_mac, status='discover')

