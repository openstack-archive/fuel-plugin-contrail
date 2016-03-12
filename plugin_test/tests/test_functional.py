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

import os
from proboscis import test
from proboscis.asserts import assert_equal
from fuelweb_test import logger
from fuelweb_test.helpers.decorators import log_snapshot_after_test
from fuelweb_test.settings import CONTRAIL_PLUGIN_PACK_UB_PATH
from fuelweb_test.tests.base_test_case import SetupEnvironment
from fuelweb_test.tests.base_test_case import TestBasic
from helpers import plugin
from helpers import openstack


@test(groups=["plugins"])
class IntegrationTests(TestBasic):
    """IntegrationTests."""

    pack_copy_path = '/var/www/nailgun/plugins/contrail-3.0'
    add_package = '/var/www/nailgun/plugins/contrail-3.0/'\
                  'repositories/ubuntu/contrail-setup*'
    ostf_msg = 'OSTF tests passed successfully.'
    cluster_id = ''
    pack_path = CONTRAIL_PLUGIN_PACK_UB_PATH
    CONTRAIL_DISTRIBUTION = os.environ.get('CONTRAIL_DISTRIBUTION')

    @test(depends_on=[SetupEnvironment.prepare_slaves_9],
          groups=["contrail_plugin_add_delete_controller_node"])
    @log_snapshot_after_test
    def contrail_plugin_add_delete_controller_node(self):
        """Verify that Controller node can be deleted
        and added after deploying

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
        plugin.prepare_contrail_plugin(self, slaves=9)

        # enable plugin in contrail settings
        plugin.activate_plugin(self)

        # activate vSRX image
        vsrx_setup_result = plugin.activate_vsrx()

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

        openstack.update_deploy_check(self,
                                      dict(conf_no_controller, **conf_ctrl),
                                      is_vsrx=vsrx_setup_result)
        openstack.update_deploy_check(self,
                                      conf_ctrl, delete=True,
                                      is_vsrx=vsrx_setup_result)
        openstack.update_deploy_check(self,
                                      conf_ctrl,
                                      is_vsrx=vsrx_setup_result)

    @test(depends_on=[SetupEnvironment.prepare_slaves_9],
          groups=["contrail_plugin_add_delete_compute_node"])
    @log_snapshot_after_test
    def contrail_plugin_add_delete_compute_node(self):
        """Verify that Compute node can be deleted and added after deploying

        Scenario:
            1. Create an environment with
               "Neutron with tunneling segmentation"
               as a network configuration and CEPH storage
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
        plugin.prepare_contrail_plugin(self, slaves=9)

        # enable plugin in contrail settings
        plugin.activate_plugin(self)

        # activate vSRX image
        vsrx_setup_result = plugin.activate_vsrx()

        conf_no_controller = {
            'slave-01': ['controller'],
            'slave-02': ['controller'],
            'slave-03': ['controller'],
            'slave-04': ['controller'],
            'slave-05': ['compute', 'cinder'],
            'slave-06': ['compute', 'cinder'],
            'slave-07': ['compute', 'cinder'],
            # Here slave-8
            'slave-09': ['contrail-db',
                         'contrail-config',
                         'contrail-control'],

        }
        conf_compute = {'slave-08': ['compute', 'cinder']}

        openstack.update_deploy_check(self,
                                      dict(conf_no_controller, **conf_compute),
                                      is_vsrx=vsrx_setup_result)
        openstack.update_deploy_check(self,
                                      conf_compute, delete=True,
                                      is_vsrx=vsrx_setup_result)
        openstack.update_deploy_check(self, conf_compute,
                                      is_vsrx=vsrx_setup_result)

    @test(depends_on=[SetupEnvironment.prepare_slaves_9],
          groups=["contrail_ha_with_shutdown_contrail_node"])
    @log_snapshot_after_test
    def contrail_ha_with_shutdown_contrail_node(self):
        """Verify HA with deleting Contrail roles

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
            9. Deploy changes
            10. Run OSTF tests
            11. Check Controller and Contrail nodes status

        """
        plugin.prepare_contrail_plugin(self, slaves=9)
        plugin.activate_plugin(self)  # enable plugin in contrail settings
        vsrx_setup_result = plugin.activate_vsrx()  # activate vSRX image

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
            """Checks node state by it's name"""
            for node in self.fuel_web.client.list_cluster_nodes(cluster_id):
                if node_name in node['name']:
                    assert_equal(node['status'], node_state,
                                 'Nailgun node status is not %s but %s' % (
                                     node_state, node['status']))

        # Deploy cluster and run OSTF
        openstack.update_deploy_check(self,
                                      dict(conf_no_contrail,
                                           **conf_contrail),
                                      is_vsrx=vsrx_setup_result)

        # Check all nodes are 'ready'
        for node_name in dict(conf_no_contrail, **conf_contrail):
            check_node_state(self.cluster_id, node_name, 'ready')

        # Shutdown contrail node
        for node in self.fuel_web.client.list_cluster_nodes(self.cluster_id):
            if 'slave-06' in node['name']:
                logger.info('Shutdown node "%s"' % node['name'])
                self.fuel_web.warm_shutdown_nodes(
                    self.fuel_web.get_devops_nodes_by_nailgun_nodes([node]))
                break

        # Run OSTF tests again
        if vsrx_setup_result:
            self.fuel_web.run_ostf(cluster_id=self.cluster_id)

        # Check controller and contrail nodes states
        node_roles = {'controller', 'contrail-config'}
        for node_name, roles in conf_no_contrail.items():
            if node_roles & set(roles):
                check_node_state(self.cluster_id, node_name, 'ready')

    @test(depends_on=[SetupEnvironment.prepare_slaves_5],
          groups=["contrail_add_control"])
    @log_snapshot_after_test
    def contrail_add_control(self):
        """Verify that Contrail control role can be added after deploying

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
        plugin.prepare_contrail_plugin(self, slaves=5)

        # enable plugin in contrail settings
        plugin.activate_plugin(self)

        # activate vSRX image
        vsrx_setup_result = plugin.activate_vsrx()

        conf_nodes = {
            'slave-01': ['controller'],
            'slave-02': ['compute'],
            'slave-03': ['contrail-control',
                         'contrail-config',
                         'contrail-db'],
        }
        conf_control = {'slave-04': ['contrail-control']}

        openstack.update_deploy_check(self, conf_nodes,
                                      is_vsrx=vsrx_setup_result)

        openstack.update_deploy_check(self, conf_control,
                                      is_vsrx=vsrx_setup_result)

    @test(depends_on=[SetupEnvironment.prepare_slaves_5],
          groups=["contrail_add_config"])
    @log_snapshot_after_test
    def contrail_add_config(self):
        """Verify that Contrail config role can be added after deploying

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
        plugin.prepare_contrail_plugin(self, slaves=5)

        # enable plugin in contrail settings
        plugin.activate_plugin(self)

        # activate vSRX image
        vsrx_setup_result = plugin.activate_vsrx()

        conf_nodes = {
            'slave-01': ['controller'],
            'slave-02': ['compute'],
            'slave-03': ['contrail-control',
                         'contrail-config',
                         'contrail-db'],
        }
        conf_config = {'slave-04': ['contrail-config']}

        openstack.update_deploy_check(self, conf_nodes,
                                      is_vsrx=vsrx_setup_result)

        openstack.update_deploy_check(self, conf_config,
                                      is_vsrx=vsrx_setup_result)

    @test(depends_on=[SetupEnvironment.prepare_slaves_5],
          groups=["contrail_delete_control"])
    @log_snapshot_after_test
    def contrail_delete_control(self):
        """Verify that Contrail control role can be deleted after deploying

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
        plugin.prepare_contrail_plugin(self, slaves=5)

        # enable plugin in contrail settings
        plugin.activate_plugin(self)

        # activate vSRX image
        vsrx_setup_result = plugin.activate_vsrx()

        conf_no_control = {
            'slave-01': ['controller'],
            'slave-02': ['compute'],
            'slave-03': ['contrail-control',
                         'contrail-config',
                         'contrail-db'],
            # Here slave-4
        }
        conf_control = {'slave-04': ['contrail-control']}

        openstack.update_deploy_check(self,
                                      dict(conf_no_control, **conf_control),
                                      is_vsrx=vsrx_setup_result)
        openstack.update_deploy_check(self,
                                      conf_control, delete=True,
                                      is_vsrx=vsrx_setup_result)

    @test(depends_on=[SetupEnvironment.prepare_slaves_5],
          groups=["contrail_delete_config"])
    @log_snapshot_after_test
    def contrail_delete_config(self):
        """Verify that Contrail config role can be deleted after deploying

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
        plugin.prepare_contrail_plugin(self, slaves=5)

        # enable plugin in contrail settings
        plugin.activate_plugin(self)

        # activate vSRX image
        vsrx_setup_result = plugin.activate_vsrx()

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

        openstack.update_deploy_check(self,
                                      dict(conf_no_config, **conf_config),
                                      is_vsrx=vsrx_setup_result)
        openstack.update_deploy_check(self,
                                      conf_config, delete=True,
                                      is_vsrx=vsrx_setup_result)

    @test(depends_on=[SetupEnvironment.prepare_slaves_5],
          groups=["contrail_add_del_db"])
    @log_snapshot_after_test
    def contrail_add_del_db(self):
        """Verify that Contrail DB role can be added and deleted after
        deploying

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
            10. Delete node with "contrail-db", which was added before
            11. Deploy changes
            12. Run OSTF tests
            13. Check Controller and Contrail nodes status

        """
        plugin.prepare_contrail_plugin(self, slaves=5)

        # enable plugin in contrail settings
        plugin.activate_plugin(self)

        # activate vSRX image
        vsrx_setup_result = plugin.activate_vsrx()

        conf_no_db = {
            'slave-01': ['controller'],
            'slave-02': ['compute'],
            'slave-03': ['contrail-control',
                         'contrail-config',
                         'contrail-db'],
            # Here slave-4
        }
        conf_db = {'slave-04': ['contrail-db']}

        openstack.update_deploy_check(self,
                                      conf_no_db,
                                      is_vsrx=vsrx_setup_result)
        openstack.update_deploy_check(self,
                                      conf_db,
                                      is_vsrx=vsrx_setup_result)
        openstack.update_deploy_check(self,
                                      conf_db, delete=True,
                                      is_vsrx=vsrx_setup_result)

    @test(depends_on=[SetupEnvironment.prepare_slaves_5],
          groups=["contrail_db_multirole"])
    @log_snapshot_after_test
    def contrail_db_multirole(self):
        """Deploy Environment with Contrail DB + Ceph multirole

        Scenario:
            1. Create an environment with "Neutron with tunneling
               segmentation" as a network configuration
            2. Enable and configure Contrail plugin
            3. Add some controller, compute nodes
            4. Add 1 node with "contrail-db" + "Ceph-OSD" role, one
               node with "contrail-control" + "storage-cinder" and
               1 node with "contrail-config" + "Ceph-OSD"
            5. Deploy cluster
            6. Run OSTF tests

        """
        plugin.prepare_contrail_plugin(self, slaves=5)

        # enable plugin in contrail settings
        plugin.activate_plugin(self)

        # activate vSRX image
        vsrx_setup_result = plugin.activate_vsrx()

        conf_db = {
            'slave-01': ['controller'],
            'slave-02': ['compute'],
            'slave-03': ['contrail-db',
                         'ceph-osd'],
            'slave-04': ['contrail-control',
                         'cinder'],
            'slave-05': ['contrail-config',
                         'ceph-osd']
        }

        openstack.update_deploy_check(self,
                                      conf_db,
                                      is_vsrx=vsrx_setup_result)

    @test(depends_on=[SetupEnvironment.prepare_slaves_5],
          groups=["contrail_control_multirole"])
    @log_snapshot_after_test
    def contrail_control_multirole(self):
        """Deploy Environment with Contrail Control  + Ceph multirole

        Scenario:
            1. Create an environment with "Neutron with tunneling
               segmentation" as a network configuration
            2. Enable and configure Contrail plugin
            3. Add some controller, compute + "Ceph-OSD" nodes
            4. Add 1 node with "contrail-control" + "contrail-config" +
               "Ceph-OSD" multirole and 1 node with "contrail-db" +
               "storage-cinder"
            5. Deploy cluster
            6. Run OSTF tests

        """
        plugin.prepare_contrail_plugin(self, slaves=5)

        # enable plugin in contrail settings
        plugin.activate_plugin(self)

        # activate vSRX image
        vsrx_setup_result = plugin.activate_vsrx()

        conf_control = {
            'slave-01': ['controller'],
            'slave-02': ['compute',
                         'ceph-osd'],
            'slave-03': ['contrail-db',
                         'cinder'],
            'slave-04': ['contrail-control',
                         'contrail-config',
                         'ceph-osd'],
        }

        openstack.update_deploy_check(self,
                                      conf_control,
                                      is_vsrx=vsrx_setup_result)

    @test(depends_on=[SetupEnvironment.prepare_slaves_5],
          groups=["contrail_config_multirole"])
    @log_snapshot_after_test
    def contrail_config_multirole(self):
        """Deploy Environment with Contrail Control  + Ceph multirole

        Scenario:
            1. Create an environment with "Neutron with tunneling
               segmentation" as a network configuration
            2. Enable and configure Contrail plugin
            3. Add some controller, compute + "Ceph-OSD" nodes
            4. Add 1 node with "contrail-config" + "Ceph-OSD" +
               "storage-cinder" multirole and one node with "contrail-db"
               + "contrail-control"
            5. Deploy cluster
            6. Run OSTF tests

        """
        plugin.prepare_contrail_plugin(self, slaves=5)

        # enable plugin in contrail settings
        plugin.activate_plugin(self)

        # activate vSRX image
        vsrx_setup_result = plugin.activate_vsrx()

        conf_config = {
            'slave-01': ['controller'],
            'slave-02': ['compute',
                         'ceph-osd'],
            'slave-03': ['contrail-db',
                         'contrail-control'],
            'slave-04': ['contrail-config',
                         'ceph-osd',
                         'cinder'],
        }

        openstack.update_deploy_check(self,
                                      conf_config,
                                      is_vsrx=vsrx_setup_result)
