"""Copyright 2016 Mirantis, Inc.

Licensed under the Apache License, Version 2.0 (the "License"); you may
not use this file except in compliance with the License. You may obtain
copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
License for the specific language governing permissions and limitations
under the License.
"""
from __future__ import division

from ipaddr import IPAddress
from ipaddr import summarize_address_range
import json
import netaddr
import os
import os.path

from devops.helpers.helpers import wait
from proboscis import asserts
from proboscis import SkipTest
from proboscis import test

from fuelweb_test.helpers.checkers import check_get_network_data_over_cli
from fuelweb_test.helpers.checkers import check_update_network_data_over_cli
from fuelweb_test.helpers.decorators import check_fuel_statistics
from fuelweb_test.helpers.decorators import log_snapshot_after_test
from fuelweb_test.helpers import utils

from fuelweb_test.settings import CONTRAIL_PLUGIN_PACK_UB_PATH
from fuelweb_test.settings import MULTIPLE_NETWORKS
from fuelweb_test.settings import NODEGROUPS
from fuelweb_test.tests.base_test_case import SetupEnvironment
from fuelweb_test.tests.test_net_templates_base import TestNetworkTemplatesBase
from fuelweb_test import logger

from helpers import plugin


@test(groups=["plugins"])
class TestMultipleNets(TestNetworkTemplatesBase):
    """IntegrationTests."""

    pack_copy_path = '/var/www/nailgun/plugins/contrail-4.0'
    add_package = \
        '/var/www/nailgun/plugins/contrail-4.0/' \
        'repositories/ubuntu/contrail-setup*'
    ostf_msg = 'OSTF tests passed successfully.'

    cluster_id = ''

    pack_path = CONTRAIL_PLUGIN_PACK_UB_PATH

    CONTRAIL_DISTRIBUTION = os.environ.get('CONTRAIL_DISTRIBUTION')

    def get_modified_ranges(self, net_dict, net_name, group_id):
        """Get modified ip range for network."""
        for net in net_dict['networks']:
            if net_name in net['name'] and net['group_id'] == group_id:
                cidr = net['cidr']
                sliced_list = list(netaddr.IPNetwork(cidr))[5:-5]
                return [str(sliced_list[0]), str(sliced_list[-1])]

    def change_default_admin_range(self, networks, number_excluded_ips):
        """Change IP range for admin net by excluding N of first addresses.

        :param networks: list, environment networks configuration
        :param number_excluded_ips: int, number of IPs to remove from range
        """
        default_admin_network = [n for n in networks
                                 if (n['name'] == "fuelweb_admin" and
                                     n['group_id'] is None)]
        asserts.assert_true(len(default_admin_network) == 1,
                            "Default 'admin/pxe' network not found "
                            "in cluster network configuration!")
        default_admin_range = [IPAddress(ip) for ip
                               in default_admin_network[0]["ip_ranges"][0]]
        new_admin_range = [default_admin_range[0] + number_excluded_ips,
                           default_admin_range[1]]
        default_admin_network[0]["ip_ranges"][0] = [str(ip)
                                                    for ip in new_admin_range]
        return default_admin_network[0]["ip_ranges"][0]

    def is_ip_in_range(self, ip_addr, ip_range_start, ip_range_end):
        """Get ip range."""
        ip_addr_ranges = summarize_address_range(IPAddress(ip_range_start),
                                                 IPAddress(ip_range_end))
        return any(IPAddress(ip_addr) in iprange for iprange in ip_addr_ranges)

    def is_update_dnsmasq_running(self, tasks):
        """Check update dnsmasq is running."""
        for task in tasks:
            if task['name'] == "update_dnsmasq" and \
               task["status"] == "running":
                return True
        return False

    def update_network_ranges(self, net_data, update_data):
        """Check network range."""
        for net in net_data['networks']:
            for group in update_data:
                for net_name in update_data[group]:
                    if net_name in net['name'] and net['group_id'] == group:
                        net['ip_ranges'] = update_data[group][net_name]
                        net['meta']['notation'] = 'ip_ranges'
        return net_data

    def get_ranges(self, net_data, net_name, group_id):
        """Get range."""
        return [
            net['ip_ranges'] for net in net_data['networks'] if
            net_name in net['name'] and group_id == net['group_id']][0]

    @test(depends_on=[SetupEnvironment.prepare_release],
          groups=["contrail_ha_multiple_nodegroups"])
    @log_snapshot_after_test
    @check_fuel_statistics
    def contrail_ha_multiple_nodegroups(self):
        """Deploy HA environment with Neutron GRE and 2 nodegroups.

        Scenario:
            1. Revert snapshot with ready master node
            2. Install contrail plugin
            3. Bootstrap slaves from default nodegroup
            4. Create cluster with Neutron GRE and custom nodegroups
            5. Activate plugin and configure plugins setings
            6. Remove 2nd custom nodegroup which is added automatically
            7. Bootstrap slave nodes from custom nodegroup
            8. Download network configuration
            9. Update network.json  with customized ip ranges
            10. Put new json on master node and update network data
            11. Verify that new IP ranges are applied for network config
            12. Add following nodes to default nodegroup:
                * 3 controller+mongo+ceph
            13. Add following nodes to custom nodegroup:
                * 1 compute
                * 1 contrail-config+contrail-control+contrail-db
            14. Deploy cluster
            15. Run network verification
            16. Verify that excluded ip is not used for nodes or VIP
            17. Run health checks (OSTF)

        Duration 2.5 hours

        """
        if not MULTIPLE_NETWORKS:
            raise SkipTest()
        self.show_step(1, initialize=True)
        self.env.revert_snapshot("ready")
        self.show_step(2)
        plugin.prepare_contrail_plugin(self, snapshot_name="ready",
                                       options={'images_ceph': True,
                                                'volumes_ceph': True,
                                                'ephemeral_ceph': True,
                                                'objects_ceph': True,
                                                'volumes_lvm': False,
                                                'ceilometer': True})

        cluster_id = self.fuel_web.get_last_created_cluster()
        self.env.bootstrap_nodes(self.env.d_env.nodes().slaves[0:3])

        plugin.activate_plugin(self)
        # activate vSRX image
        vsrx_setup_result = plugin.activate_vsrx()

        self.show_step(6)
        self.netconf_all_groups = self.fuel_web.client.get_networks(cluster_id)
        custom_group2 = self.fuel_web.get_nodegroup(
            cluster_id, name=NODEGROUPS[2]['name'])
        wait(lambda: not self.is_update_dnsmasq_running(
            self.fuel_web.client.get_tasks()), timeout=60,
            timeout_msg="Timeout exceeded while waiting for task "
                        "'update_dnsmasq' is finished!")
        self.fuel_web.client.delete_nodegroup(custom_group2['id'])

        self.show_step(7)
        self.env.bootstrap_nodes(self.env.d_env.nodes().slaves[3:5])

        self.show_step(8)
        with self.env.d_env.get_admin_remote() as remote:
            check_get_network_data_over_cli(remote, cluster_id, '/var/log/')
        management_ranges_default = []
        management_ranges_custom = []
        storage_ranges_default = []
        storage_ranges_custom = []
        default_group_id = self.fuel_web.get_nodegroup(cluster_id)['id']
        custom_group_id = self.fuel_web.get_nodegroup(
            cluster_id, name=NODEGROUPS[1]['name'])['id']

        self.show_step(9)
        with self.env.d_env.get_admin_remote() as remote:
            current_net = json.loads(remote.open(
                '/var/log/network_1.json').read())
            # Get storage ranges for default and custom groups
            storage_ranges_default.append(self.get_modified_ranges(
                current_net, 'storage', group_id=default_group_id))

            storage_ranges_custom.append(self.get_modified_ranges(
                current_net, 'storage', group_id=custom_group_id))

            management_ranges_default.append(self.get_modified_ranges(
                current_net, 'management', group_id=default_group_id))

            management_ranges_custom.append(self.get_modified_ranges(
                current_net, 'management', group_id=custom_group_id))

            update_data = {
                default_group_id: {'storage': storage_ranges_default,
                                   'management': management_ranges_default},
                custom_group_id: {'storage': storage_ranges_custom,
                                  'management': management_ranges_custom}}

            updated_network = self.update_network_ranges(
                current_net, update_data)

            logger.debug(
                'Plan to update ranges for default group to {0} for storage '
                'and {1} for management and for custom group storage {2},'
                ' management {3}'.format(storage_ranges_default,
                                         management_ranges_default,
                                         storage_ranges_custom,
                                         management_ranges_custom))

            # need to push to remote
            self.show_step(10)
            utils.put_json_on_remote_from_dict(
                remote, updated_network, cluster_id)

            check_update_network_data_over_cli(remote, cluster_id,
                                               '/var/log/')

        self.show_step(11)
        with self.env.d_env.get_admin_remote() as remote:
            check_get_network_data_over_cli(remote, cluster_id, '/var/log/')
            latest_net = json.loads(remote.open(
                '/var/log/network_1.json').read())
            updated_storage_default = self.get_ranges(latest_net, 'storage',
                                                      default_group_id)

            updated_storage_custom = self.get_ranges(latest_net, 'storage',
                                                     custom_group_id)
            updated_mgmt_default = self.get_ranges(latest_net, 'management',
                                                   default_group_id)
            updated_mgmt_custom = self.get_ranges(latest_net, 'management',
                                                  custom_group_id)

            asserts.assert_equal(
                updated_storage_default, storage_ranges_default,
                'Looks like storage range for default nodegroup '
                'was not updated. Expected {0}, Actual: {1}'.format(
                    storage_ranges_default, updated_storage_default))

            asserts.assert_equal(
                updated_storage_custom, storage_ranges_custom,
                'Looks like storage range for custom nodegroup '
                'was not updated. Expected {0}, Actual: {1}'.format(
                    storage_ranges_custom, updated_storage_custom))

            asserts.assert_equal(
                updated_mgmt_default, management_ranges_default,
                'Looks like management range for default nodegroup was '
                'not updated. Expected {0}, Actual: {1}'.format(
                    management_ranges_default, updated_mgmt_default))

            asserts.assert_equal(
                updated_mgmt_custom, management_ranges_custom,
                'Looks like management range for custom nodegroup was '
                'not updated. Expected {0}, Actual: {1}'.format(
                    management_ranges_custom, updated_mgmt_custom))

        self.show_step(12)
        self.show_step(13)
        nodegroup_default = NODEGROUPS[0]['name']
        nodegroup_custom1 = NODEGROUPS[1]['name']
        self.fuel_web.update_nodes(
            cluster_id,
            {
                'slave-01': [
                    ['controller', 'ceph-osd', 'mongo'], nodegroup_default],
                'slave-02': [
                    ['controller', 'ceph-osd', 'mongo'], nodegroup_default],
                'slave-03': [
                    ['controller', 'ceph-osd', 'mongo'], nodegroup_default],
                'slave-04': [
                    ['contrail-config', 'contrail-control', 'contrail-db'],
                    nodegroup_custom1],
                'slave-05': [['compute'], nodegroup_custom1],
            }
        )
        self.show_step(14)
        self.fuel_web.deploy_cluster_wait(cluster_id)

        self.show_step(15)
        self.fuel_web.verify_network(cluster_id)

        self.show_step(16)
        net_data_default_group = [
            data['network_data'] for data
            in self.fuel_web.client.list_cluster_nodes(
                cluster_id) if data['group_id'] == default_group_id]

        for net_node in net_data_default_group:
            for net in net_node:
                if 'storage' in net['name']:
                    asserts.assert_true(
                        self.is_ip_in_range(
                            net['ip'].split('/')[0],
                            updated_storage_default[0][0],
                            updated_storage_default[0][-1]))
                if 'management' in net['name']:
                    asserts.assert_true(
                        self.is_ip_in_range(
                            net['ip'].split('/')[0],
                            updated_mgmt_default[0][0],
                            updated_mgmt_default[0][-1]))

        net_data_custom_group = [
            data['network_data'] for data
            in self.fuel_web.client.list_cluster_nodes(
                cluster_id) if data['group_id'] == custom_group_id]

        for net_node in net_data_custom_group:
            for net in net_node:
                if 'storage' in net['name']:
                    asserts.assert_true(
                        self.is_ip_in_range(
                            net['ip'].split('/')[0],
                            updated_storage_custom[0][0],
                            updated_storage_custom[0][-1]))
                if 'management' in net['name']:
                    asserts.assert_true(
                        self.is_ip_in_range(
                            net['ip'].split('/')[0],
                            updated_mgmt_custom[0][0],
                            updated_mgmt_custom[0][-1]))

        mgmt_vrouter_vip = self.fuel_web.get_management_vrouter_vip(
            cluster_id)
        logger.debug('Management vrouter vips is {0}'.format(
            mgmt_vrouter_vip))
        mgmt_vip = self.fuel_web.get_mgmt_vip(cluster_id)
        logger.debug('Management vips is {0}'.format(mgmt_vip))
        # check for defaults
        asserts.assert_true(self.is_ip_in_range(mgmt_vrouter_vip.split('/')[0],
                                                updated_mgmt_default[0][0],
                                                updated_mgmt_default[0][-1]))
        asserts.assert_true(self.is_ip_in_range(mgmt_vip.split('/')[0],
                                                updated_mgmt_default[0][0],
                                                updated_mgmt_default[0][-1]))
        self.show_step(17)
        if vsrx_setup_result:
            self.fuel_web.run_ostf(cluster_id=cluster_id)
