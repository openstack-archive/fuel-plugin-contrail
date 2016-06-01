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
import string
import time

from random import choice
from proboscis import test
from proboscis.asserts import assert_equal
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
from helpers import plugin
from helpers import openstack
from helpers import settings


@test(groups=["plugins"])
class IntegrationTests(TestBasic):
    """IntegrationTests."""

    pack_copy_path = '/var/www/nailgun/plugins/contrail-4.0'
    add_package = '/var/www/nailgun/plugins/contrail-4.0/'\
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
            1. Create an environment with
               "Neutron with tunneling segmentation"
               as a network configuration
            2. Enable and configure Contrail plugin
            3. Add some controller (at least 3), compute and storage nodes
            4. Add 3 nodes with "contrail-db", "contarail-config" and
               "contrail-control" roles on all nodes
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
        vsrx_setup_result = plugin.activate_vsrx()

        plugin.show_range(self, 3, 5)
        conf_no_controller = {
            'slave-01': ['controller'],
            'slave-02': ['controller'],
            # Here slave-03
            'slave-04': ['compute'],
            'slave-05': ['cinder'],
            'slave-06': ['contrail-db',
                         'contrail-config',
                         'contrail-control'],
            'slave-07': ['contrail-db',
                         'contrail-config',
                         'contrail-control'],
            'slave-08': ['contrail-db',
                         'contrail-config',
                         'contrail-control'],
        }
        conf_ctrl = {'slave-03': ['controller']}

        plugin.show_range(self, 5, 7)
        openstack.update_deploy_check(self,
                                      dict(conf_no_controller, **conf_ctrl),
                                      is_vsrx=vsrx_setup_result)
        self.show_step(7)
        openstack.update_deploy_check(self,
                                      conf_ctrl, delete=True,
                                      is_vsrx=False)
        self.show_step(8)
        self.fuel_web.run_ostf(
            cluster_id=self.cluster_id,
            test_sets=['smoke', 'sanity', 'ha'],
            timeout=settings.OSFT_RUN_TIMEOUT,
            should_fail=1,
            failed_test_name=['Check that required services are running']
        )
        self.show_step(9)
        openstack.update_deploy_check(self,
                                      conf_ctrl,
                                      is_vsrx=False)
        self.show_step(10)
        self.fuel_web.run_ostf(
            cluster_id=self.cluster_id,
            test_sets=['smoke', 'ha'],
            timeout=settings.OSFT_RUN_TIMEOUT)

    @test(depends_on=[SetupEnvironment.prepare_slaves_9],
          groups=["contrail_plugin_add_delete_compute_node"])
    @log_snapshot_after_test
    def contrail_plugin_add_delete_compute_node(self):
        """Verify that Compute node can be deleted and added after deploying.

        Scenario:
            1. Create an environment with
               "Neutron with tunneling segmentation"
               as a network configuration and Cinder storage
            2. Enable and configure Contrail plugin
            3. Add some controller, compute + storage (at least 4) nodes
            4. Add a node with "contrail-db", "contarail-config" and
               "contrail-control" roles
            5. Deploy cluster
            6. Run OSTF tests
            7. Delete a compute node and deploy changes
            8. Run OSTF tests
            9. Add a node with "compute" role and deploy changes
            10. Run OSTF tests

        """
        self.show_step(1)
        plugin.prepare_contrail_plugin(self, slaves=9)

        self.show_step(2)
        plugin.activate_plugin(self)

        # activate vSRX image
        vsrx_setup_result = plugin.activate_vsrx()

        plugin.show_range(self, 3, 5)
        conf_no_controller = {
            'slave-01': ['controller'],
            'slave-02': ['controller'],
            'slave-03': ['controller'],
            'slave-05': ['compute', 'cinder'],
            'slave-06': ['compute', 'cinder'],
            'slave-07': ['compute', 'cinder'],
            # Here slave-8
            'slave-09': ['contrail-db',
                         'contrail-config',
                         'contrail-control'],

        }
        conf_compute = {'slave-08': ['compute', 'cinder']}

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
            timeout=settings.OSFT_RUN_TIMEOUT,
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
            timeout=settings.OSFT_RUN_TIMEOUT)

    @test(depends_on=[SetupEnvironment.prepare_slaves_9],
          groups=["contrail_ha_with_shutdown_contrail_node"])
    @log_snapshot_after_test
    def contrail_ha_with_shutdown_contrail_node(self):
        """Verify HA with deleting Contrail roles.

        Scenario:
            1. Create an environment with
               "Neutron with tunneling segmentation"
               as a network configuration
            2. Enable and configure Contrail plugin
            3. Add some controller, compute and storage nodes
            4. Add 4 nodes with "contrail-db", "contarail-config" and
               "contrail-control" roles
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
        vsrx_setup_result = plugin.activate_vsrx()  # activate vSRX image

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
                         'contrail-control'],
            'slave-08': ['contrail-db',
                         'contrail-config',
                         'contrail-control'],
            'slave-09': ['contrail-db',
                         'contrail-config',
                         'contrail-control'],

        }
        conf_contrail = {
            'slave-06': ['contrail-db',
                         'contrail-config',
                         'contrail-control']
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
            1. Create an environment with "Neutron with tunneling
               segmentation" as a network configuration
            2. Enable and configure Contrail plugin
            3. Add some controller, compute nodes
            4. Add 1 node with "contrail-control", "contrail-config"
               and "contrail-db" roles
            5. Deploy cluster
            6. Run OSTF tests
            7. Check Controller and Contrail nodes status
            8. Add one node with "contrail-control" role
            9. Deploy changes
            10. Run OSTF tests
            11. Check Controller and Contrail nodes status

        """
        self.show_step(1)
        plugin.prepare_contrail_plugin(self, slaves=5)

        self.show_step(2)
        plugin.activate_plugin(self)

        # activate vSRX image
        vsrx_setup_result = plugin.activate_vsrx()

        plugin.show_range(self, 3, 5)
        conf_nodes = {
            'slave-01': ['controller'],
            'slave-02': ['compute'],
            'slave-03': ['contrail-control',
                         'contrail-config',
                         'contrail-db'],
        }
        conf_control = {'slave-04': ['contrail-control']}

        plugin.show_range(self, 5, 7)
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
            1. Create an environment with "Neutron with tunneling
               segmentation" as a network configuration
            2. Enable and configure Contrail plugin
            3. Add some controller, compute nodes
            4. Add 1 node with "contrail-control", "contrail-config"
               and "contrail-db" roles
            5. Deploy cluster
            6. Run OSTF tests
            7. Check Controller and Contrail nodes status
            8. Add one node with "contrail-config" role
            9. Deploy changes
            10. Run OSTF tests
            11. Check Controller and Contrail nodes status

        """
        self.show_step(1)
        plugin.prepare_contrail_plugin(self, slaves=5)

        self.show_step(2)
        plugin.activate_plugin(self)

        # activate vSRX image
        vsrx_setup_result = plugin.activate_vsrx()

        plugin.show_range(self, 3, 5)
        conf_nodes = {
            'slave-01': ['controller'],
            'slave-02': ['compute'],
            'slave-03': ['contrail-control',
                         'contrail-config',
                         'contrail-db'],
        }
        conf_config = {'slave-04': ['contrail-config']}

        plugin.show_range(self, 5, 7)
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
            1. Create an environment with "Neutron with tunneling
               segmentation" as a network configuration
            2. Enable and configure Contrail plugin
            3. Add some controller, compute nodes
            4. Add 1 node with "contrail-control", "contrail-config" and
               "contrail-db" roles and 1 node with "contrail-control" role
            5. Deploy cluster
            6. Run OSTF tests
            7. Check Controller and Contrail nodes status
            8. Delete one "contrail-control" role
            9. Deploy changes
            10. Run OSTF tests
            11. Check Controller and Contrail nodes status

        """
        self.show_step(1)
        plugin.prepare_contrail_plugin(self, slaves=5)

        self.show_step(2)
        plugin.activate_plugin(self)

        # activate vSRX image
        vsrx_setup_result = plugin.activate_vsrx()

        plugin.show_range(self, 3, 5)
        conf_no_control = {
            'slave-01': ['controller'],
            'slave-02': ['compute'],
            'slave-03': ['contrail-control',
                         'contrail-config',
                         'contrail-db'],
            # Here slave-4
        }
        conf_control = {'slave-04': ['contrail-control']}

        plugin.show_range(self, 5, 7)
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
            1. Create an environment with "Neutron with tunneling
               segmentation" as a network configuration
            2. Enable and configure Contrail plugin
            3. Add some controller, compute nodes
            4. Add 1 node with "contrail-control", "contrail-config" and
               1 node with "contrail-config", "contrail-db" and 1 node with
               "contrail-config" roles
            5. Deploy cluster
            6. Run OSTF tests
            7. Check Controller and Contrail nodes status
            8. Delete one "contrail-config" role
            9. Deploy changes
            10. Run OSTF tests
            11. Check Controller and Contrail nodes status

        """
        self.show_step(1)
        plugin.prepare_contrail_plugin(self, slaves=5)

        self.show_step(2)
        plugin.activate_plugin(self)

        # activate vSRX image
        vsrx_setup_result = plugin.activate_vsrx()

        plugin.show_range(self, 3, 5)
        conf_no_config = {
            'slave-01': ['controller'],
            'slave-02': ['compute'],
            'slave-03': ['contrail-control',
                         'contrail-config'],
            'slave-04': ['contrail-config',
                         'contrail-db'],
            # Here slave-5
        }
        conf_config = {'slave-05': ['contrail-config']}

        plugin.show_range(self, 5, 7)
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
        """Verify that Contrail DB role can be added and deleted after deploy.

        Scenario:
            1. Create an environment with "Neutron with tunneling
               segmentation" as a network configuration
            2. Enable and configure Contrail plugin
            3. Add some controller, compute nodes
            4. Add 1 node with "contrail-control", "contrail-config" and
               "contrail-db" roles
            5. Deploy cluster
            6. Check Controller and Contrail nodes status
            7. Add one node with "contrail-db" role
            8. Deploy changes
            9. Run OSTF tests

        """
        self.show_step(1)
        plugin.prepare_contrail_plugin(self, slaves=5)

        self.show_step(2)
        plugin.activate_plugin(self)

        # activate vSRX image
        vsrx_setup_result = plugin.activate_vsrx()

        plugin.show_range(self, 3, 5)
        conf_no_db = {
            'slave-01': ['controller'],
            'slave-02': ['compute'],
            'slave-03': ['contrail-control',
                         'contrail-config',
                         'contrail-db'],
            # Here slave-4
        }
        conf_db = {'slave-04': ['contrail-db']}

        self.show_step(5)
        openstack.update_deploy_check(self,
                                      conf_no_db,
                                      is_vsrx=vsrx_setup_result)
        plugin.show_range(self, 7, 10)
        openstack.update_deploy_check(self,
                                      conf_db,
                                      is_vsrx=vsrx_setup_result)

    @test(depends_on=[SetupEnvironment.prepare_slaves_5],
          groups=["contrail_plugin_add_delete_compute_ceph"])
    @log_snapshot_after_test
    def contrail_plugin_add_delete_compute_ceph(self):
        """Verify that compute node can be added and deleted in env with Ceph.

        Scenario:
            1. Create an environment with "Neutron with tunneling
               segmentation" as a network configuration
            2. Enable and configure Contrail plugin
            3. Add 1 node with "controller" + "mongo" roles and
               3 nodes with "compute" + "ceph-osd" roles
            4. Add node with "contrail-control", "contrail-config" and
               "contrail-db" roles
            5. Deploy cluster and run OSTF tests
            6. Check Controller and Contrail nodes status
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
        vsrx_setup_result = plugin.activate_vsrx()

        plugin.show_range(self, 3, 5)
        conf_no_db = {
            'slave-01': ['controller', 'mongo'],
            'slave-02': ['compute', 'ceph-osd'],
            'slave-03': ['compute', 'ceph-osd'],
            'slave-04': ['compute', 'ceph-osd'],
            'slave-05': ['contrail-control',
                         'contrail-config',
                         'contrail-db'],
            # Here slave-6
        }
        conf_db = {'slave-06': ['compute']}

        self.show_step(5)
        openstack.update_deploy_check(self, conf_no_db,
                                      is_vsrx=vsrx_setup_result)
        plugin.show_range(self, 7, 9)
        openstack.update_deploy_check(self, conf_db,
                                      is_vsrx=vsrx_setup_result)
        plugin.show_range(self, 9, 12)
        openstack.update_deploy_check(
            self, conf_db, delete=True,
            is_vsrx=vsrx_setup_result,
            ostf_fail_tests=['Check that required services are running'])

    @test(depends_on=[SetupEnvironment.prepare_slaves_3],
          groups=["contrail_login_password"])
    @log_snapshot_after_test
    def contrail_login_password(self):
        """Create a new network via Contrail.

        Scenario:
            1. Deploy cluster with Contrail.
            2. Login as admin to Openstack Horizon UI.
            3. Create new user.
            4. Login as user to Openstack Horizon UI.
            5. Change login and password for user.
            6. Login to Openstack Horizon UI with new credentials.
            7. Login to Contrail Ui with same credentials.

        Duration: 15 min

        """
        # constants
        max_password_lengh = 64
        port = 18082

        self.show_step(1)
        plugin.prepare_contrail_plugin(self, slaves=3)

        # activate vSRX image
        plugin.activate_vsrx()

        plugin.activate_plugin(self)
        cluster_id = self.fuel_web.get_last_created_cluster()

        plugin.change_contrail_api_port(self, port)

        self.fuel_web.update_nodes(
            self.cluster_id,
            {
                'slave-01': ['contrail-config',
                             'contrail-control',
                             'contrail-db'],
                'slave-02': ['controller'],
                'slave-03': ['compute'],
            })

        openstack.deploy_cluster(self)
        self.fuel_web.run_ostf(
            cluster_id=self.cluster_id, test_sets=['smoke'])

        self.show_step(2)
        os_ip = self.fuel_web.get_public_vip(cluster_id)
        os_conn = os_actions.OpenStackActions(
            os_ip, SERVTEST_USERNAME,
            SERVTEST_PASSWORD,
            SERVTEST_TENANT)
        contrail_client = ContrailClient(os_ip, contrail_port=port)
        projects = contrail_client.get_projects()

        tenant = os_conn.get_tenant(SERVTEST_TENANT)

        self.show_step(3)
        chars = string.letters + string.digits + string.punctuation
        new_password = ''.join(
            [choice(chars) for i in range(max_password_lengh)])
        new_username = ''.join(
            [choice(chars) for i in range(max_password_lengh)])
        logger.info(
            'New username: {0}, new password: {1}'.format(
                new_username, new_password))
        new_user = os_conn.create_user(new_username, new_password, tenant)
        role = [role for role in os_conn.keystone.roles.list()
                if role.name == 'admin'].pop()
        os_conn.keystone.roles.add_user_role(new_user.id, role.id, tenant.id)

        self.show_step(4)
        os_actions.OpenStackActions(
            os_ip, new_username,
            new_password,
            SERVTEST_TENANT)

        self.show_step(5)
        new_password = ''.join(
            [choice(chars) for i in range(max_password_lengh)])
        new_user.manager.update_password(new_user, new_password)
        logger.info(
            'New username: {0}, new password: {1}'.format(
                new_username, new_password))
        time.sleep(30)  # need to update password for new user

        self.show_step(6)
        os_actions.OpenStackActions(
            os_ip, new_username,
            new_password,
            SERVTEST_TENANT)
        contrail = ContrailClient(
            os_ip, contrail_port=port,
            credentials={
                'username': new_username,
                'tenant_name': SERVTEST_TENANT,
                'password': new_password})

        assert_equal(
            projects, contrail.get_projects(),
            "Can not give info by Contrail API.")
