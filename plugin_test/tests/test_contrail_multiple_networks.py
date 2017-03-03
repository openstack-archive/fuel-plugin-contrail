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

import json
import os
import os.path

from proboscis import asserts
from proboscis import SkipTest
from proboscis import test

from devops.helpers.helpers import wait

from fuelweb_test import logger
from fuelweb_test.helpers.checkers import check_get_network_data_over_cli
from fuelweb_test.helpers.checkers import check_update_network_data_over_cli
from fuelweb_test.helpers.decorators import check_fuel_statistics
from fuelweb_test.helpers.decorators import log_snapshot_after_test
from fuelweb_test.settings import CONTRAIL_PLUGIN_PACK_UB_PATH
from fuelweb_test.settings import MULTIPLE_NETWORKS
from fuelweb_test.settings import NODEGROUPS
from fuelweb_test.tests.base_test_case import SetupEnvironment
from fuelweb_test.tests.test_multiple_networks import TestMultipleClusterNets

from helpers import vsrx
from helpers import plugin
from helpers import openstack
from helpers import settings
from tests.test_contrail_check import TestContrailCheck


@test(groups=["contrail_multiple_networks"])
class TestMultipleNets(TestMultipleClusterNets):
    """TestMultipleNets."""

    pack_copy_path = '/var/www/nailgun/plugins/contrail-5.1'
    add_package = \
        '/var/www/nailgun/plugins/contrail-5.1/' \
        'repositories/ubuntu/contrail-setup*'
    ostf_msg = 'OSTF tests passed successfully.'

    cluster_id = ''

    pack_path = CONTRAIL_PLUGIN_PACK_UB_PATH

    CONTRAIL_DISTRIBUTION = os.environ.get('CONTRAIL_DISTRIBUTION')

    def update_network_config(self, cluster_id):
        """Update network configuration."""
        check_get_network_data_over_cli(
            self.ssh_manager.admin_ip, cluster_id, '/var/log/')
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

            self.show_step(10)
            with remote.open(
                    '/var/log/network_{0}.json'.format(cluster_id),
                    mode='w') as file_obj:
                json.dump(updated_network, file_obj)
            check_update_network_data_over_cli(
                self.ssh_manager.admin_ip, cluster_id, '/var/log/')

            self.show_step(11)
            check_get_network_data_over_cli(
                self.ssh_manager.admin_ip, cluster_id, '/var/log/')
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

        return updated_storage_default, updated_storage_custom, \
            updated_mgmt_default, updated_mgmt_custom

    @test(depends_on=[SetupEnvironment.prepare_release],
          groups=["contrail_ha_multiple_networks"])
    @log_snapshot_after_test
    @check_fuel_statistics
    def contrail_ha_multiple_networks(self):
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
                * 3 controller+ceph
                * 1 compute
            13. Add following nodes to custom nodegroup:
                * 1 contrail-controller
                * 1 contrail-analytics-db+contrail-analytics
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
        plugin.show_range(self, 2, 6)
        plugin.prepare_contrail_plugin(self, snapshot_name="ready",
                                       options={'images_ceph': True,
                                                'volumes_ceph': True,
                                                'ephemeral_ceph': True,
                                                'objects_ceph': True,
                                                'volumes_lvm': False})

        cluster_id = self.fuel_web.get_last_created_cluster()
        self.env.bootstrap_nodes(self.env.d_env.nodes().slaves[0:3])

        plugin.activate_plugin(self)
        # activate vSRX image
        vsrx_setup_result = vsrx.activate(self, vsrx_config=True)

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
        self.env.bootstrap_nodes(self.env.d_env.nodes().slaves[3:6])

        self.show_step(8)
        updated_storage_default, updated_storage_custom, \
            updated_mgmt_default, updated_mgmt_custom = \
            self.update_network_config(cluster_id)

        self.show_step(12)
        self.show_step(13)
        nodegroup_default = NODEGROUPS[0]['name']
        nodegroup_custom1 = NODEGROUPS[1]['name']
        default_group_id = self.fuel_web.get_nodegroup(cluster_id)['id']
        custom_group_id = self.fuel_web.get_nodegroup(
            cluster_id, name=NODEGROUPS[1]['name'])['id']
        self.fuel_web.update_nodes(
            cluster_id,
            {
                'slave-01': [
                    ['controller', 'ceph-osd'], nodegroup_default],
                'slave-02': [
                    ['controller', 'ceph-osd'], nodegroup_default],
                'slave-03': [
                    ['controller', 'ceph-osd'], nodegroup_default],
                'slave-04': [
                    ['contrail-controller'], nodegroup_custom1],
                'slave-05': [['compute'], nodegroup_custom1],
                'slave-06': [
                    ['contrail-analytics-db', 'contrail-analytics'],
                    nodegroup_custom1],
            }
        )
        self.show_step(14)
        openstack.deploy_cluster(self)
        TestContrailCheck(self).cloud_check(['contrail'])

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
            self.fuel_web.run_ostf(
                cluster_id=cluster_id,
                test_sets=['smoke', 'sanity', 'ha'],
                timeout=settings.OSTF_RUN_TIMEOUT)

    @test(depends_on=[SetupEnvironment.prepare_release],
          groups=["contrail_multiple_networks_add_controller"])
    @log_snapshot_after_test
    @check_fuel_statistics
    def contrail_multiple_networks_add_controller(self):
        """Check Contrail deploy multiple networks add controller.

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
            12. Add following nodes to custom nodegroup:
                * 1 controller+mongo
            13. Add following nodes to default nodegroup:
                * 1 compute
                * 1 contrail-controller+contrail-analytics
                * 1 contrail-analytics-db
                * 1 cinder
            14. Deploy cluster
            15. Run health checks (OSTF)
            16. Add 1 controller node
            17. Redeploy cluster
            18. Run health checks (OSTF)

        Duration 2.5 hours

        """
        if not MULTIPLE_NETWORKS:
            raise SkipTest()
        self.show_step(1, initialize=True)
        self.env.revert_snapshot("ready")
        plugin.show_range(self, 2, 6)
        plugin.prepare_contrail_plugin(self, snapshot_name="ready",
                                       options={'ceilometer': True})

        cluster_id = self.fuel_web.get_last_created_cluster()
        self.env.bootstrap_nodes(self.env.d_env.nodes().slaves[0:3])

        plugin.activate_plugin(self)
        # activate vSRX image
        vsrx_setup_result = vsrx.activate(self, vsrx_config=True)

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
        self.env.bootstrap_nodes(self.env.d_env.nodes().slaves[3:6])

        self.show_step(8)
        updated_storage_default, updated_storage_custom, \
            updated_mgmt_default, updated_mgmt_custom = \
            self.update_network_config(cluster_id)

        self.show_step(12)
        self.show_step(13)
        nodegroup_default = NODEGROUPS[0]['name']
        nodegroup_custom1 = NODEGROUPS[1]['name']
        self.fuel_web.update_nodes(
            cluster_id,
            {
                'slave-01': [
                    ['contrail-controller', 'contrail-analytics'],
                    nodegroup_default],
                'slave-02': [['contrail-analytics-db'], nodegroup_default],
                'slave-03': [['compute'], nodegroup_default],
                'slave-04': [['cinder'], nodegroup_default],
                'slave-05': [['controller', 'mongo'], nodegroup_custom1],
            }
        )

        self.show_step(14)
        openstack.deploy_cluster(self)
        TestContrailCheck(self).cloud_check(['contrail'])

        self.show_step(15)
        if vsrx_setup_result:
            self.fuel_web.run_ostf(
                cluster_id=self.cluster_id,
                test_sets=['smoke', 'sanity', 'tests_platform'],
                timeout=settings.OSTF_RUN_TIMEOUT
            )

        self.show_step(16)
        self.fuel_web.update_nodes(
            cluster_id,
            {'slave-06': [['controller'], nodegroup_custom1], }
        )

        self.show_step(17)
        openstack.deploy_cluster(self)
        TestContrailCheck(self).cloud_check(['contrail'])

        self.show_step(18)
        if vsrx_setup_result:
            self.fuel_web.run_ostf(
                cluster_id=self.cluster_id,
                test_sets=['smoke', 'sanity', 'tests_platform'],
                timeout=settings.OSTF_RUN_TIMEOUT
            )

    @test(depends_on=[SetupEnvironment.prepare_release],
          groups=["contrail_multiple_networks_delete_controller"])
    @log_snapshot_after_test
    @check_fuel_statistics
    def contrail_multiple_networks_delete_controller(self):
        """Check Contrail deploy multiple networks remove controller.

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
                * 1 controller+cinder
                * 1 controller
            13. Add following nodes to custom nodegroup:
                * 1 compute
                * 1 contrail-controller
                * 1 contrail-analytics
                * 1 contrail-analytics-db
            14. Deploy cluster
            15. Run health checks (OSTF)
            16. Remove 1 controller node
            17. Redeploy cluster
            18. Run health checks (OSTF)

        Duration 2.5 hours

        """
        if not MULTIPLE_NETWORKS:
            raise SkipTest()
        self.show_step(1, initialize=True)
        self.env.revert_snapshot("ready")
        plugin.show_range(self, 2, 6)
        plugin.prepare_contrail_plugin(self, snapshot_name="ready")

        cluster_id = self.fuel_web.get_last_created_cluster()
        self.env.bootstrap_nodes(self.env.d_env.nodes().slaves[0:2])

        plugin.activate_plugin(self)
        # activate vSRX image
        vsrx_setup_result = vsrx.activate(self, vsrx_config=True)

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
        self.env.bootstrap_nodes(self.env.d_env.nodes().slaves[2:6])

        self.show_step(8)
        updated_storage_default, updated_storage_custom, \
            updated_mgmt_default, updated_mgmt_custom = \
            self.update_network_config(cluster_id)

        self.show_step(12)
        self.show_step(13)
        nodegroup_default = NODEGROUPS[0]['name']
        nodegroup_custom1 = NODEGROUPS[1]['name']
        self.fuel_web.update_nodes(
            cluster_id,
            {
                'slave-01': [['controller', 'cinder'], nodegroup_custom1],
                'slave-02': [['controller'], nodegroup_custom1],
                'slave-03': [['contrail-analytics-db'], nodegroup_default],
                'slave-04': [['compute', 'cinder'], nodegroup_default],
                'slave-05': [['contrail-controller'], nodegroup_default],
                'slave-06': [['contrail-analytics'], nodegroup_default],
            }
        )
        self.show_step(14)
        openstack.deploy_cluster(self)
        TestContrailCheck(self).cloud_check(['contrail'])

        self.show_step(15)
        if vsrx_setup_result:
            self.fuel_web.run_ostf(
                cluster_id=self.cluster_id,
                test_sets=['smoke', 'sanity', 'ha'],
                timeout=settings.OSTF_RUN_TIMEOUT
            )

        self.show_step(16)
        conf_control = {'slave-02': [['controller'], nodegroup_custom1]}

        plugin.show_range(self, 17, 18)
        openstack.update_deploy_check(
            self, conf_control, delete=True,
            is_vsrx=vsrx_setup_result,
            ostf_fail_tests=['Check that required services are running'])

        TestContrailCheck(self).cloud_check(['contrail'])

    @test(depends_on=[SetupEnvironment.prepare_release],
          groups=["contrail_multiple_networks_delete_compute"])
    @log_snapshot_after_test
    @check_fuel_statistics
    def contrail_multiple_networks_delete_compute(self):
        """Check Contrail deploy multiple networks remove compute.

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
                * 1 controller
                * 2 compute
            13. Add following nodes to custom nodegroup:
                * 1 contrail-controller
                * 1 contrail-analytics
                * 1 contrail-analytics-db
            14. Deploy cluster
            15. Run health checks (OSTF)
            16. Remove 1 compute node
            17. Redeploy cluster
            18. Run health checks (OSTF)

        Duration 2.5 hours

        """
        if not MULTIPLE_NETWORKS:
            raise SkipTest()
        self.show_step(1, initialize=True)
        self.env.revert_snapshot("ready")
        plugin.show_range(self, 2, 6)
        plugin.prepare_contrail_plugin(self, snapshot_name="ready")

        cluster_id = self.fuel_web.get_last_created_cluster()
        self.env.bootstrap_nodes(self.env.d_env.nodes().slaves[0:3])

        plugin.activate_plugin(self)
        # activate vSRX image
        vsrx_setup_result = vsrx.activate(self, vsrx_config=True)

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
        self.env.bootstrap_nodes(self.env.d_env.nodes().slaves[3:6])

        self.show_step(8)
        updated_storage_default, updated_storage_custom, \
            updated_mgmt_default, updated_mgmt_custom = \
            self.update_network_config(cluster_id)

        self.show_step(12)
        self.show_step(13)
        nodegroup_default = NODEGROUPS[0]['name']
        nodegroup_custom1 = NODEGROUPS[1]['name']
        self.fuel_web.update_nodes(
            cluster_id,
            {
                'slave-01': [['controller'], nodegroup_default],
                'slave-02': [['compute'], nodegroup_default],
                'slave-03': [['compute'], nodegroup_default],
                'slave-04': [
                    ['contrail-controller'], nodegroup_custom1],
                'slave-05': [['contrail-analytics'], nodegroup_custom1],
                'slave-06': [['contrail-analytics-db'], nodegroup_custom1],
            }
        )
        self.show_step(14)
        openstack.deploy_cluster(self)
        TestContrailCheck(self).cloud_check(['contrail'])

        self.show_step(15)
        if vsrx_setup_result:
            self.fuel_web.run_ostf(
                cluster_id=cluster_id,
                test_sets=['smoke', 'sanity', 'ha'],
                timeout=settings.OSTF_RUN_TIMEOUT)

        self.show_step(16)
        conf_compute = {'slave-03': [['compute'], nodegroup_custom1], }

        plugin.show_range(self, 17, 18)
        openstack.update_deploy_check(
            self, conf_compute, delete=True,
            is_vsrx=vsrx_setup_result,
            ostf_fail_tests=['Check that required services are running'])

        TestContrailCheck(self).cloud_check(['contrail'])

    @test(depends_on=[SetupEnvironment.prepare_release],
          groups=["contrail_multiple_networks_add_compute"])
    @log_snapshot_after_test
    @check_fuel_statistics
    def contrail_multiple_networks_add_compute(self):
        """Check Contrail deploy multiple networks add compute.

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
                * 1 controller
            13. Add following nodes to custom nodegroup:
                * 1 compute+ceph-osd
                * 1 contrail-controller+contrail-analytics
                * 1 contrail-analytics-db
            14. Deploy cluster
            15. Run health checks (OSTF)
            16. Add 1 compute node
            17. Redeploy cluster
            18. Run health checks (OSTF)

        Duration 2.5 hours

        """
        if not MULTIPLE_NETWORKS:
            raise SkipTest()
        self.show_step(1, initialize=True)
        self.env.revert_snapshot("ready")
        plugin.show_range(self, 2, 6)
        plugin.prepare_contrail_plugin(
            self, snapshot_name="ready",
            options={
                'images_ceph': True,
                'volumes_ceph': True,
                'ephemeral_ceph': True,
                'objects_ceph': True,
                'volumes_lvm': False,
                'osd_pool_size': '1'})

        cluster_id = self.fuel_web.get_last_created_cluster()
        self.env.bootstrap_nodes(self.env.d_env.nodes().slaves[0:1])

        plugin.activate_plugin(self)
        # activate vSRX image
        vsrx_setup_result = vsrx.activate(self, vsrx_config=True)

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
        self.env.bootstrap_nodes(self.env.d_env.nodes().slaves[1:5])

        self.show_step(8)
        updated_storage_default, updated_storage_custom, \
            updated_mgmt_default, updated_mgmt_custom = \
            self.update_network_config(cluster_id)

        plugin.show_range(self, 12, 14)
        nodegroup_default = NODEGROUPS[0]['name']
        nodegroup_custom1 = NODEGROUPS[1]['name']
        self.fuel_web.update_nodes(
            cluster_id,
            {
                'slave-01': [['controller'], nodegroup_default],
                'slave-02': [
                    ['contrail-controller', 'contrail-analytics'],
                    nodegroup_custom1],
                'slave-03': [['contrail-analytics-db'], nodegroup_custom1],
                'slave-04': [['compute', 'ceph-osd'], nodegroup_custom1],
            }
        )
        self.show_step(14)
        openstack.deploy_cluster(self)
        TestContrailCheck(self).cloud_check(['contrail'])

        self.show_step(15)
        if vsrx_setup_result:
            self.fuel_web.run_ostf(cluster_id=cluster_id)

        self.show_step(16)
        conf_compute = {'slave-05': [['compute'], nodegroup_custom1]}

        self.fuel_web.update_nodes(cluster_id, conf_compute)

        self.show_step(17)
        openstack.deploy_cluster(self)
        TestContrailCheck(self).cloud_check(['contrail'])

        self.show_step(18)
        if vsrx_setup_result:
            self.fuel_web.run_ostf(
                cluster_id=cluster_id,
                test_sets=['smoke', 'sanity', 'ha'],
                timeout=settings.OSTF_RUN_TIMEOUT)

    @test(depends_on=[SetupEnvironment.prepare_release],
          groups=["contrail_different_ha_in_multinet"])
    @log_snapshot_after_test
    @check_fuel_statistics
    def contrail_different_ha_in_multinet(self):
        """Check Contrail deploy multiple networks with contrail HA.

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
                * 1 controller
                * 2 contrail-controller+contrail-analytics
            13. Add following nodes to custom nodegroup:
                * 1 cinder
                * 1 ccontrail-controller+ contrail-analytics
                * 1 contrail-analytics-db
            14. Deploy cluster
            15. Run health checks (OSTF)

        Duration 2.5 hours

        """
        if not MULTIPLE_NETWORKS:
            raise SkipTest()
        self.show_step(1, initialize=True)
        self.env.revert_snapshot("ready")
        plugin.show_range(self, 2, 6)
        plugin.prepare_contrail_plugin(self, snapshot_name="ready")

        cluster_id = self.fuel_web.get_last_created_cluster()
        self.env.bootstrap_nodes(self.env.d_env.nodes().slaves[0:3])

        plugin.activate_plugin(self)
        # activate vSRX image
        vsrx_setup_result = vsrx.activate(self, vsrx_config=True)

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
        self.env.bootstrap_nodes(self.env.d_env.nodes().slaves[3:6])

        self.show_step(8)
        updated_storage_default, updated_storage_custom, \
            updated_mgmt_default, updated_mgmt_custom = \
            self.update_network_config(cluster_id)

        plugin.show_range(self, 9, 14)
        nodegroup_default = NODEGROUPS[0]['name']
        nodegroup_custom1 = NODEGROUPS[1]['name']
        self.fuel_web.update_nodes(
            cluster_id,
            {
                'slave-01': [
                    ['controller'], nodegroup_default],
                'slave-02': [['compute'], nodegroup_default],
                'slave-03': [
                    ['contrail-controller', 'contrail-analytics'],
                    nodegroup_default],
                'slave-04': [
                    ['contrail-controller', 'contrail-analytics'],
                    nodegroup_custom1],
                'slave-05': [
                    ['contrail-controller', 'contrail-analytics'],
                    nodegroup_custom1],
                'slave-06': [
                    ['contrail-analytics-db'], nodegroup_custom1],
            }
        )
        self.show_step(14)
        openstack.deploy_cluster(self)
        TestContrailCheck(self).cloud_check(['contrail'])

        self.show_step(15)
        if vsrx_setup_result and settings.VSRX_CONFIG_PATH:
            self.fuel_web.run_ostf(
                cluster_id=cluster_id,
                test_sets=['smoke', 'sanity'],
                timeout=settings.OSTF_RUN_TIMEOUT)
