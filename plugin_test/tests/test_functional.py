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

import os

from proboscis import test
from proboscis.asserts import assert_equal
from proboscis.asserts import assert_true

from fuelweb_test import logger
from fuelweb_test.helpers.decorators import log_snapshot_after_test
from fuelweb_test.helpers import os_actions
from fuelweb_test.settings import CONTRAIL_PLUGIN_PACK_UB_PATH
from fuelweb_test.tests.base_test_case import SetupEnvironment
from fuelweb_test.tests.base_test_case import TestBasic
from fuelweb_test.settings import SERVTEST_PASSWORD
from fuelweb_test.settings import SERVTEST_TENANT
from fuelweb_test.settings import SERVTEST_USERNAME

from helpers.contrail_client import ContrailClient
from helpers import vsrx
from helpers import plugin
from helpers import openstack
from helpers import settings
from tests.test_contrail_check import TestContrailCheck


@test(groups=["contrail_functional_tests"])
class FunctionalTests(TestBasic):
    """IntegrationTests."""

    pack_copy_path = '/var/www/nailgun/plugins/contrail-5.0'
    add_package = '/var/www/nailgun/plugins/contrail-5.0/'\
                  'repositories/ubuntu/contrail-setup*'
    ostf_msg = 'OSTF tests passed successfully.'
    cluster_id = ''
    pack_path = CONTRAIL_PLUGIN_PACK_UB_PATH
    CONTRAIL_DISTRIBUTION = os.environ.get('CONTRAIL_DISTRIBUTION')

    @test(depends_on=[SetupEnvironment.prepare_slaves_9],
          groups=["contrail_plugin_add_delete_controller_node"])
    @log_snapshot_after_test
    def contrail_plugin_add_delete_controller_node(self):
        """Verify that Controller node can be deleted and added after deploying.

        Scenario:
            1. Create an environment
            2. Enable and configure Contrail plugin
            3. Add 3 controllers, a compute and a storage nodes
            4. Add 3 nodes with "contrail-db", "contrail-config",
               "contrail-analytics" and "contrail-control" roles on all nodes
            5. Deploy cluster
            6. Run OSTF tests
            7. Delete a Controller node and deploy changes
            8. Run OSTF tests
            9. Add a node with "Controller" role and deploy changes
            10. Run OSTF tests. All steps must be completed successfully,
                without any errors.
        """
        self.show_step(1)
        plugin.prepare_contrail_plugin(self, slaves=9)

        self.show_step(2)
        plugin.activate_plugin(self)

        # activate vSRX image
        vsrx_setup_result = vsrx.activate()

        plugin.show_range(self, 3, 5)
        conf_no_controller = {
            'slave-01': ['controller'],
            'slave-02': ['controller'],
            # Here slave-03
            'slave-04': ['compute'],
            'slave-05': ['cinder'],
            'slave-06': ['contrail-db',
                         'contrail-config',
                         'contrail-control',
                         'contrail-analytics'],
            'slave-07': ['contrail-db',
                         'contrail-config',
                         'contrail-control',
                         'contrail-analytics'],
            'slave-08': ['contrail-db',
                         'contrail-config',
                         'contrail-control',
                         'contrail-analytics'],
        }
        conf_ctrl = {'slave-03': ['controller']}

        plugin.show_range(self, 5, 7)
        openstack.update_deploy_check(self,
                                      dict(conf_no_controller, **conf_ctrl),
                                      is_vsrx=vsrx_setup_result)
        plugin.show_range(self, 7, 9)
        openstack.update_deploy_check(self,
                                      conf_ctrl, delete=True,
                                      is_vsrx=vsrx_setup_result)
        plugin.show_range(self, 9, 11)
        openstack.update_deploy_check(self,
                                      conf_ctrl,
                                      is_vsrx=vsrx_setup_result)

    @test(depends_on=[SetupEnvironment.prepare_slaves_5],
          groups=["contrail_plugin_add_delete_compute_node"])
    @log_snapshot_after_test
    def contrail_plugin_add_delete_compute_node(self):
        """Verify that Compute node can be deleted and added after deploying.

        Scenario:
            1. Create an environment
            2. Enable and configure Contrail plugin
            3. Add a controller and 3 compute + storage nodes
            4. Add a node with "contrail-db", "contarail-config",
               "contrail-analytics" and "contrail-control" roles
            5. Deploy cluster
            6. Run OSTF tests
            7. Delete a compute node and deploy changes
            8. Run OSTF tests
            9. Add a node with "compute" role and deploy changes
            10. Run OSTF tests

        """
        self.show_step(1)
        plugin.prepare_contrail_plugin(self, slaves=5)

        self.show_step(2)
        plugin.activate_plugin(self)

        # activate vSRX image
        vsrx_setup_result = vsrx.activate()

        plugin.show_range(self, 3, 5)
        conf_no_controller = {
            'slave-01': ['controller'],
            'slave-02': ['compute', 'cinder'],
            'slave-03': ['compute', 'cinder'],
            # Here slave-4
            'slave-05': ['contrail-db',
                         'contrail-config',
                         'contrail-control',
                         'contrail-analytics'],

        }
        conf_compute = {'slave-04': ['compute', 'cinder']}

        plugin.show_range(self, 5, 7)
        openstack.update_deploy_check(self,
                                      dict(conf_no_controller, **conf_compute),
                                      is_vsrx=vsrx_setup_result)
        self.show_step(7)
        openstack.update_deploy_check(self,
                                      conf_compute, delete=True,
                                      is_vsrx=False)
        self.show_step(8)
        self.fuel_web.run_ostf(
            cluster_id=self.cluster_id,
            test_sets=['smoke', 'sanity', 'ha'],
            timeout=settings.OSTF_RUN_TIMEOUT,
            should_fail=1,
            failed_test_name=['Check that required services are running']
        )
        self.show_step(9)
        openstack.update_deploy_check(self, conf_compute,
                                      is_vsrx=False)
        self.show_step(10)
        self.fuel_web.run_ostf(
            cluster_id=self.cluster_id,
            test_sets=['smoke', 'ha'],
            timeout=settings.OSTF_RUN_TIMEOUT)

    @test(depends_on=[SetupEnvironment.prepare_slaves_9],
          groups=["contrail_ha_with_shutdown_contrail_node"])
    @log_snapshot_after_test
    def contrail_ha_with_shutdown_contrail_node(self):
        """Verify HA with deleting Contrail roles.

        Scenario:
            1. Create an environment
            2. Enable and configure Contrail plugin
            3. Add some controller, compute and storage nodes
            4. Add 3 nodes with "contrail-db", "contarail-config"
               "contrail-analytics" and "contrail-control" roles
            5. Deploy cluster
            6. Run OSTF tests
            7. Check Controller and Contrail nodes status
            8. Shutdown node with 'contrail-db', "contarail-config" and
               "contrail-control" roles
            9. Run OSTF tests
            10. Check Controller and Contrail nodes status

        """
        self.show_step(1)
        plugin.prepare_contrail_plugin(self, slaves=9)
        self.show_step(2)
        plugin.activate_plugin(self)
        vsrx_setup_result = vsrx.activate()

        plugin.show_range(self, 3, 5)
        conf_no_contrail = {
            'slave-01': ['controller'],
            'slave-02': ['controller'],
            'slave-03': ['controller'],
            'slave-04': ['compute'],
            'slave-05': ['cinder'],
            # Here slave-06 with contrail
            'slave-07': ['contrail-db',
                         'contrail-config',
                         'contrail-control',
                         'contrail-analytics'],
            'slave-08': ['contrail-db',
                         'contrail-config',
                         'contrail-control',
                         'contrail-analytics']
        }
        conf_contrail = {
            'slave-06': ['contrail-db',
                         'contrail-config',
                         'contrail-control',
                         'contrail-analytics']
        }

        def check_node_state(cluster_id, node_name, node_state):
            """Check node state by it's name."""
            for node in self.fuel_web.client.list_cluster_nodes(cluster_id):
                if node_name in node['name']:
                    assert_equal(node['status'], node_state,
                                 'Nailgun node status is not %s but %s' % (
                                     node_state, node['status']))

        plugin.show_range(self, 5, 7)
        openstack.update_deploy_check(self,
                                      dict(conf_no_contrail,
                                           **conf_contrail),
                                      is_vsrx=vsrx_setup_result,
                                      ostf_suites=['smoke', 'sanity', 'ha'])

        self.show_step(7)
        for node_name in dict(conf_no_contrail, **conf_contrail):
            check_node_state(self.cluster_id, node_name, 'ready')

        self.show_step(8)
        for node in self.fuel_web.client.list_cluster_nodes(self.cluster_id):
            if 'slave-06' in node['name']:
                logger.info('Shutdown node "%s"' % node['name'])
                self.fuel_web.warm_shutdown_nodes(
                    self.fuel_web.get_devops_nodes_by_nailgun_nodes([node]))
                break

        self.show_step(9)
        if vsrx_setup_result:
            self.fuel_web.run_ostf(
                cluster_id=self.cluster_id,
                test_sets=['smoke', 'sanity', 'ha'],
                should_fail=1,
                failed_test_name=[
                    'Check state of haproxy backends on controllers'])

        self.show_step(10)
        node_roles = {'controller', 'contrail-config'}
        for node_name, roles in conf_no_contrail.items():
            if node_roles & set(roles):
                check_node_state(self.cluster_id, node_name, 'ready')

    @test(depends_on=[SetupEnvironment.prepare_slaves_5],
          groups=["contrail_add_control"])
    @log_snapshot_after_test
    def contrail_add_control(self):
        """Verify that Contrail control role can be added after deploying.

        Scenario:
            1. Create an environment
            2. Enable and configure Contrail plugin
            3. Add a controller and a compute+cinder nodes
            4. Add a node with "contrail-control" and "contrail-db" roles
            5. Add a node with "contrail-config" and "contrail-analytics" roles
            6. Deploy cluster
            7. Run OSTF tests
            8. Add one node with "contrail-control" role
            9. Deploy changes
            10. Run OSTF tests

        """
        self.show_step(1)
        plugin.prepare_contrail_plugin(self, slaves=5)

        self.show_step(2)
        plugin.activate_plugin(self)

        # activate vSRX image
        vsrx_setup_result = vsrx.activate()

        plugin.show_range(self, 3, 6)
        conf_nodes = {
            'slave-01': ['controller'],
            'slave-02': ['compute', 'cinder'],
            'slave-03': ['contrail-control',
                         'contrail-db'],
            'slave-04': ['contrail-config',
                         'contrail-analytics']
        }
        conf_control = {'slave-05': ['contrail-control']}

        plugin.show_range(self, 6, 8)
        openstack.update_deploy_check(self, conf_nodes,
                                      is_vsrx=vsrx_setup_result)

        plugin.show_range(self, 8, 11)
        openstack.update_deploy_check(self, conf_control,
                                      is_vsrx=vsrx_setup_result)

    @test(depends_on=[SetupEnvironment.prepare_slaves_5],
          groups=["contrail_add_config"])
    @log_snapshot_after_test
    def contrail_add_config(self):
        """Verify that Contrail config role can be added after deploying.

        Scenario:
            1. Create an environment
            2. Enable and configure Contrail plugin
            3. Add a controller and a compute+cinder nodes
            4. Add a node with "contrail-config" and "contrail-db" roles
            5. Add a "contrail-control"+"contrail-analytics" node
            6. Deploy cluster
            7. Run OSTF tests
            8. Add one node with "contrail-config" role
            9. Deploy changes
            10. Run OSTF tests

        """
        self.show_step(1)
        plugin.prepare_contrail_plugin(self, slaves=5)

        self.show_step(2)
        plugin.activate_plugin(self)

        # activate vSRX image
        vsrx_setup_result = vsrx.activate()

        plugin.show_range(self, 3, 6)
        conf_nodes = {
            'slave-01': ['controller'],
            'slave-02': ['compute'],
            'slave-03': ['contrail-config',
                         'contrail-db'],
            'slave-04': ['contrail-control',
                         'contrail-analytics']
        }
        conf_config = {'slave-05': ['contrail-config']}

        plugin.show_range(self, 6, 8)
        openstack.update_deploy_check(self, conf_nodes,
                                      is_vsrx=vsrx_setup_result)

        plugin.show_range(self, 8, 11)
        openstack.update_deploy_check(self, conf_config,
                                      is_vsrx=vsrx_setup_result)

    @test(depends_on=[SetupEnvironment.prepare_slaves_5],
          groups=["contrail_delete_control"])
    @log_snapshot_after_test
    def contrail_delete_control(self):
        """Verify that Contrail control role can be deleted after deploying.

        Scenario:
            1. Create an environment
            2. Enable and configure Contrail plugin
            3. Add a controller and a compute+cinder nodes
            4. Add a node with all contrail roles
            5. Add a node with "contrail-control" role
            6. Deploy cluster
            7. Run OSTF tests
            8. Delete one "contrail-control" role
            9. Deploy changes
            10. Run OSTF tests

        """
        self.show_step(1)
        plugin.prepare_contrail_plugin(self, slaves=5)

        self.show_step(2)
        plugin.activate_plugin(self)

        # activate vSRX image
        vsrx_setup_result = vsrx.activate()

        plugin.show_range(self, 3, 6)
        conf_no_control = {
            'slave-01': ['controller'],
            'slave-02': ['compute', 'cinder'],
            'slave-03': ['contrail-control',
                         'contrail-config',
                         'contrail-db',
                         'contrail-analytics'],
            # Here slave-4
        }
        conf_control = {'slave-04': ['contrail-control']}

        plugin.show_range(self, 6, 8)
        openstack.update_deploy_check(self,
                                      dict(conf_no_control, **conf_control),
                                      is_vsrx=vsrx_setup_result)
        plugin.show_range(self, 8, 11)
        openstack.update_deploy_check(self,
                                      conf_control, delete=True,
                                      is_vsrx=vsrx_setup_result)

    @test(depends_on=[SetupEnvironment.prepare_slaves_5],
          groups=["contrail_delete_config"])
    @log_snapshot_after_test
    def contrail_delete_config(self):
        """Verify that Contrail config role can be deleted after deploying.

        Scenario:
            1. Create an environment
            2. Enable and configure Contrail plugin
            3. Add a controller and a compute+cinder nodes
            4. Add a node with all contrail roles
            5. Add a node with "contrail-config" role
            6. Deploy cluster
            7. Run OSTF tests
            8. Delete one "contrail-config" role
            9. Deploy changes
            10. Run OSTF tests

        """
        self.show_step(1)
        plugin.prepare_contrail_plugin(self, slaves=5)

        self.show_step(2)
        plugin.activate_plugin(self)

        # activate vSRX image
        vsrx_setup_result = vsrx.activate()

        plugin.show_range(self, 3, 6)
        conf_no_config = {
            'slave-01': ['controller'],
            'slave-02': ['compute', 'cinder'],
            'slave-03': ['contrail-control',
                         'contrail-config',
                         'contrail-db',
                         'contrail-analytics'],
            # Here slave-4
        }
        conf_config = {'slave-04': ['contrail-config']}

        plugin.show_range(self, 6, 8)
        openstack.update_deploy_check(self,
                                      dict(conf_no_config, **conf_config),
                                      is_vsrx=vsrx_setup_result)
        plugin.show_range(self, 8, 11)
        openstack.update_deploy_check(self,
                                      conf_config, delete=True,
                                      is_vsrx=vsrx_setup_result)

    @test(depends_on=[SetupEnvironment.prepare_slaves_5],
          groups=["contrail_add_db"])
    @log_snapshot_after_test
    def contrail_add_db(self):
        """Verify that Contrail DB role can be added after deploy.

        Scenario:
            1. Create an environment
            2. Enable and configure Contrail plugin
            3. Add a controller and a compute+cinder nodes
            4. Add a node with all contrail roles
            5. Deploy cluster
            6. Add one node with "contrail-db" role
            7. Deploy changes
            8. Run OSTF tests

        """
        self.show_step(1)
        plugin.prepare_contrail_plugin(self, slaves=5)

        self.show_step(2)
        plugin.activate_plugin(self)

        # activate vSRX image
        vsrx_setup_result = vsrx.activate()

        plugin.show_range(self, 3, 5)
        conf_no_db = {
            'slave-01': ['controller'],
            'slave-02': ['compute', 'cinder'],
            'slave-03': ['contrail-control',
                         'contrail-config',
                         'contrail-db',
                         'contrail-analytics'],
            # Here slave-4
        }
        conf_db = {'slave-04': ['contrail-db']}

        self.show_step(5)
        openstack.update_deploy_check(self,
                                      conf_no_db,
                                      is_vsrx=vsrx_setup_result)
        plugin.show_range(self, 6, 9)
        openstack.update_deploy_check(self,
                                      conf_db,
                                      is_vsrx=vsrx_setup_result)

    @test(depends_on=[SetupEnvironment.prepare_slaves_9],
          groups=["contrail_add_delete_compute_ceph"])
    @log_snapshot_after_test
    def contrail_add_delete_compute_ceph(self):
        """Verify that compute node can be added and deleted in env with Ceph.

        Scenario:
            1. Create an environment
            2. Enable and configure Contrail plugin
            3. Add a node with "controller" + "mongo" roles
            4. Add 3 nodes with "compute" + "ceph-osd" roles
            5. Add a node with all contrail roles
            6. Deploy cluster and run OSTF tests
            7. Add node with "compute" role
            8. Deploy changes and run OSTF tests
            9. Delete node with "compute" role
            10. Deploy changes
            11. Run OSTF tests

        """
        self.show_step(1)
        plugin.prepare_contrail_plugin(self, slaves=9,
                                       options={
                                           'images_ceph': True,
                                           'volumes_ceph': True,
                                           'ephemeral_ceph': True,
                                           'objects_ceph': True,
                                           'ceilometer': True,
                                           'volumes_lvm': False})
        self.show_step(2)
        plugin.activate_plugin(self)
        # activate vSRX image
        vsrx_setup_result = vsrx.activate()

        plugin.show_range(self, 3, 6)
        conf_no_compute = {
            'slave-01': ['controller', 'mongo'],
            'slave-02': ['compute', 'ceph-osd'],
            'slave-03': ['compute', 'ceph-osd'],
            'slave-04': ['compute', 'ceph-osd'],
            'slave-05': ['contrail-control',
                         'contrail-config',
                         'contrail-db',
                         'contrail-analytics'],
            # Here slave-6
        }
        conf_compute = {'slave-06': ['compute']}

        self.show_step(6)
        openstack.update_deploy_check(self, conf_no_compute,
                                      is_vsrx=vsrx_setup_result)
        plugin.show_range(self, 7, 9)
        openstack.update_deploy_check(self, conf_compute,
                                      is_vsrx=vsrx_setup_result)
        plugin.show_range(self, 9, 12)
        openstack.update_deploy_check(
            self, conf_compute, delete=True,
            is_vsrx=vsrx_setup_result)

    @test(depends_on=[SetupEnvironment.prepare_slaves_3],
          groups=["contrail_no_default"])
    @log_snapshot_after_test
    def contrail_no_default(self):
        """Check configured no default contrail parameters via Contrail WEB.

        Scenario:
            1. Install contrail plugin.
            2. Create cluster.
            3. Set following no defaults contrail parameters:
               *contrail_api_port
               *contrail_route_target
               *contrail_gateways
               *contrail_external
               *contrail_asnum
            4. Add nodes:
                1 all contrail-specified roles
                1 controller
                1 compute
            5. Deploy cluster.
            6. Verify that all configured contrail parameters present in
               the Contrail WEB.

        Duration: 2.5 hours

        """
        # constants
        contrail_api_port = 18082
        contrail_route_target = 4294967295
        contrail_gateways = '10.109.3.250'
        contrail_external = '10.10.1.0/24'
        contrail_asnum = 65534
        external_net = 'admin_floating_net'

        self.show_step(1)
        self.show_step(2)
        plugin.prepare_contrail_plugin(self, slaves=3)

        # activate vSRX image
        vsrx.activate()

        self.show_step(3)
        plugin.activate_plugin(
            self, contrail_api_public_port=contrail_api_port,
            contrail_route_target=contrail_route_target,
            contrail_gateways=contrail_gateways,
            contrail_external=contrail_external,
            contrail_asnum=contrail_asnum)

        cluster_id = self.fuel_web.get_last_created_cluster()

        self.show_step(4)
        self.fuel_web.update_nodes(
            self.cluster_id,
            {
                'slave-01': ['contrail-config',
                             'contrail-control',
                             'contrail-db',
                             'contrail-analytics'],
                'slave-02': ['controller'],
                'slave-03': ['compute'],
            })

        self.show_step(5)
        openstack.deploy_cluster(self)
        TestContrailCheck(self).cloud_check(['contrail'])

        self.show_step(6)
        os_ip = self.fuel_web.get_public_vip(cluster_id)
        os_conn = os_actions.OpenStackActions(
            os_ip, SERVTEST_USERNAME,
            SERVTEST_PASSWORD,
            SERVTEST_TENANT)
        contrail_client = ContrailClient(
            os_ip, contrail_port=contrail_api_port)

        logger.info(
            'Check contrail_asnum, contrail_route_target via Contrail.')
        external_net_id = os_conn.get_network(external_net)['id']
        ext_net = contrail_client.get_net_by_id(
            external_net_id)["virtual-network"]
        fuel_router_target = '{0}:{1}'.format(
            contrail_asnum, contrail_route_target)
        contrail_router_target = ext_net['route_target_list']['route_target']
        message = 'Parameters {0} from Fuel is not equel {1} from Contrail Web'
        assert_true(
            fuel_router_target in contrail_router_target[0],
            message.format(fuel_router_target, contrail_router_target[0]))

        logger.info('Check contrail_external via Contrail.')
        external_ip = ext_net[
            'network_ipam_refs'][0]['attr']['ipam_subnets'][0]['subnet']
        assert_true(
            contrail_external.split('/')[0] == external_ip['ip_prefix'],
            message.format(
                contrail_external.split('/')[0],
                external_ip['ip_prefix']
            )
        )
        assert_true(
            contrail_external.split('/')[1] == str(
                external_ip['ip_prefix_len']),
            message.format(
                contrail_external.split('/')[1],
                external_ip['ip_prefix_len'])
        )

        logger.info('Check contrail_gateways via Contrail.')
        bgp_ids = contrail_client.get_bgp_routers()['bgp-routers']

        bgp_ips = [
            contrail_client.get_bgp_by_id(bgp_id['uuid'])[
                'bgp-router']['bgp_router_parameters']['address']
            for bgp_id in bgp_ids]

        assert_true(
            contrail_gateways in bgp_ips,
            message.format(contrail_gateways, bgp_ips))

    @test(depends_on=[SetupEnvironment.prepare_slaves_5],
          groups=["contrail_add_analytics"])
    @log_snapshot_after_test
    def contrail_add_analytics(self):
        """Verify that Contrail-Analytics role can be added after deploy.

        Scenario:
            1. Create an environment
            2. Enable and configure Contrail plugin
            3. Add a controller and a compute+cinder nodes
            4. Add a node with "contrail-config" and "contrail-control" roles
            5. Add a "contrail-db"+"contrail-analytics" node
            6. Deploy cluster
            7. Run OSTF tests
            8. Add one node with "contrail-analytics" role
            9. Deploy changes
            10. Run OSTF tests

        """
        self.show_step(1)
        plugin.prepare_contrail_plugin(self, slaves=5)

        self.show_step(2)
        plugin.activate_plugin(self)

        # activate vSRX image
        vsrx_setup_result = vsrx.activate()

        plugin.show_range(self, 3, 6)
        conf_nodes = {
            'slave-01': ['controller'],
            'slave-02': ['compute', 'cinder'],
            'slave-03': ['contrail-config',
                         'contrail-control'],
            'slave-04': ['contrail-db',
                         'contrail-analytics']
        }
        conf_config = {'slave-05': ['contrail-analytics']}

        plugin.show_range(self, 6, 8)
        openstack.update_deploy_check(self, conf_nodes,
                                      is_vsrx=vsrx_setup_result)

        plugin.show_range(self, 8, 11)
        openstack.update_deploy_check(self, conf_config,
                                      is_vsrx=vsrx_setup_result)

    @test(depends_on=[SetupEnvironment.prepare_slaves_5],
          groups=["contrail_delete_analytics"])
    @log_snapshot_after_test
    def contrail_delete_analytics(self):
        """Verify that Contrail analytics role can be deleted after deploying.

        Scenario:
            1. Create an environment
            2. Enable and configure Contrail plugin
            3. Add a controller and a compute+cinder nodes
            4. Add a node with all contrail roles
            5. Add a node with "contrail-analytics" role
            6. Deploy cluster
            7. Run OSTF tests
            8. Delete one "contrail-analytics" role
            9. Deploy changes
            10. Run OSTF tests

        """
        self.show_step(1)
        plugin.prepare_contrail_plugin(self, slaves=5)

        self.show_step(2)
        plugin.activate_plugin(self)

        # activate vSRX image
        vsrx_setup_result = vsrx.activate()

        plugin.show_range(self, 3, 6)
        conf_no_config = {
            'slave-01': ['controller'],
            'slave-02': ['compute', 'cinder'],
            'slave-03': ['contrail-control',
                         'contrail-config',
                         'contrail-db',
                         'contrail-analytics'],
            # Here slave-4
        }
        conf_config = {'slave-04': ['contrail-analytics']}

        plugin.show_range(self, 6, 8)
        openstack.update_deploy_check(self,
                                      dict(conf_no_config, **conf_config),
                                      is_vsrx=vsrx_setup_result)
        plugin.show_range(self, 8, 11)
        openstack.update_deploy_check(self,
                                      conf_config, delete=True,
                                      is_vsrx=vsrx_setup_result)

    @test(depends_on=[SetupEnvironment.prepare_slaves_9],
          groups=["contrail_add_all_contrail"])
    @log_snapshot_after_test
    def contrail_add_all_contrail(self):
        """Verify that after deploying can be added an all contrail roles node.

        Scenario:
            1. Create an environment with Ceph-OSD storage
            2. Enable and configure Contrail plugin
            3. Add 3 nodes with "controller" + "ceph-osd" roles
            4. Add 2 nodes with "compute" + "ceph-osd" roles
            5. Add a node with all contrail roles
            6. Deploy cluster and run OSTF tests
            7. Add a node with all contrail roles
            8. Deploy changes and run OSTF tests

        """
        self.show_step(1)
        plugin.prepare_contrail_plugin(self, slaves=9,
                                       options={
                                           'images_ceph': True,
                                           'volumes_ceph': True,
                                           'ephemeral_ceph': True,
                                           'objects_ceph': True,
                                           'volumes_lvm': False})
        self.show_step(2)
        plugin.activate_plugin(self)
        # activate vSRX image
        vsrx_setup_result = vsrx.activate()

        plugin.show_range(self, 3, 6)
        conf_no_ha_contrail = {
            'slave-01': ['controller', 'ceph-osd'],
            'slave-02': ['controller', 'ceph-osd'],
            'slave-03': ['compute', 'ceph-osd'],
            'slave-04': ['compute', 'ceph-osd'],
            'slave-05': ['compute', 'ceph-osd'],
            'slave-06': ['contrail-control',
                         'contrail-config',
                         'contrail-db',
                         'contrail-analytics'],
            # Here slave-6
        }
        conf_ha_contrail = {'slave-07': ['contrail-control',
                                         'contrail-config',
                                         'contrail-db',
                                         'contrail-analytics']}

        self.show_step(6)
        openstack.update_deploy_check(self, conf_no_ha_contrail,
                                      is_vsrx=vsrx_setup_result)
        plugin.show_range(self, 7, 9)
        openstack.update_deploy_check(self, conf_ha_contrail,
                                      is_vsrx=vsrx_setup_result)

    @test(depends_on=[SetupEnvironment.prepare_slaves_5],
          groups=["contrail_ostf_net_provisioning_disable"])
    @log_snapshot_after_test
    def contrail_ostf_net_provisioning_disable(self):
        """Verify that we can disable OSTF networks provisioning.

        Scenario:
            1. Create an environment
            2. Enable and configure Contrail plugin without
               OSTF network provisioning
            3. Add a controller and a compute+cinder nodes
            4. Add a node with "contrail-config" and "contrail-control" roles
            5. Add a "contrail-db"+"contrail-analytics" node
            6. Deploy cluster
            7. Run OSTF tests
            8. Check Controller and Contrail nodes status

        """
        self.show_step(1)
        plugin.prepare_contrail_plugin(self, slaves=5)

        self.show_step(2)

        # Disable OSTF networks provisioning
        opts = {
            'provision_networks': False,
        }
        plugin.activate_plugin(self, **opts)

        # activate vSRX image
        vsrx_setup_result = vsrx.activate()

        plugin.show_range(self, 3, 6)
        conf_nodes = {
            'slave-01': ['controller'],
            'slave-02': ['compute', 'cinder'],
            'slave-03': ['contrail-config',
                         'contrail-control'],
            'slave-04': ['contrail-db',
                         'contrail-analytics']
        }

        plugin.show_range(self, 6, 8)
        should_fails = [
            'Create volume and boot instance from it',
            'Launch instance, create snapshot, launch instance from snapshot',
            'Launch instance with file injection',
            'Launch instance',
            'Create volume and attach it to instance',
            'Check network connectivity from instance via floating IP']
        openstack.update_deploy_check(
            self, conf_nodes,
            is_vsrx=vsrx_setup_result,
            ostf_fail_tests=should_fails)
