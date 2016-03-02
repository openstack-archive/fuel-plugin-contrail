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
import time
from proboscis.asserts import assert_equal, assert_is_none
from proboscis import test
from fuelweb_test import logger
from fuelweb_test.helpers.decorators import log_snapshot_after_test
from fuelweb_test.settings import CONTRAIL_PLUGIN_PACK_UB_PATH
from fuelweb_test.tests.base_test_case import SetupEnvironment
from fuelweb_test.tests.base_test_case import TestBasic
from helpers import plugin
from helpers import openstack


@test(groups=["plugins"])
class FailoverTests(TestBasic):
    """FailoverTests."""

    pack_copy_path = '/var/www/nailgun/plugins/contrail-3.0'
    add_package = '/var/www/nailgun/plugins/contrail-3.0/'\
                  'repositories/ubuntu/contrail-setup*'
    ostf_msg = 'OSTF tests passed successfully.'
    cluster_id = ''
    pack_path = CONTRAIL_PLUGIN_PACK_UB_PATH
    CONTRAIL_DISTRIBUTION = os.environ.get('CONTRAIL_DISTRIBUTION')

    @test(depends_on=[SetupEnvironment.prepare_slaves_3],
          groups=["cannot_deploy_only_contrail_db"])
    @log_snapshot_after_test
    def cannot_deploy_only_contrail_db(self):
        """Check can not deploy Contrail cluster with "contrail_db" only

        Scenario:
            1. Create an environment with
               "Neutron with tunneling segmentation"
               as a network configuration
            2. Enable and configure Contrail plugin
            3. Add 1 node with "Controller" and 1 node with "Compute" role
            4. Add 1 nodes with "contrail-db" role
            5. Deploy cluster and verify that it will fail
        """

        plugin.prepare_contrail_plugin(self, slaves=3)

        # enable plugin in contrail settings
        plugin.activate_plugin(self)

        self.fuel_web.update_nodes(
            self.cluster_id,
            {
                'slave-01': ['controller'],
                'slave-02': ['compute'],
                'slave-03': ['contrail-db']
            })

        openstack.deploy_cluster(self, wait_for_status='error')
        cluster_info = self.fuel_web.client.get_cluster(self.cluster_id)
        assert_equal(cluster_info['status'], 'error'), "Error was expected"

    @test(depends_on=[SetupEnvironment.prepare_slaves_3],
          groups=["cannot_deploy_only_contrail_config"])
    @log_snapshot_after_test
    def cannot_deploy_only_contrail_config(self):
        """Check can not deploy Contrail cluster with "contrail_config" only

        Scenario:
            1. Create an environment with
               "Neutron with tunneling segmentation"
               as a network configuration
            2. Enable and configure Contrail plugin
            3. Add 1 node with "Controller" and 1 node with "Compute" role
            4. Add 1 nodes with "contrail-config" role
            5. Deploy cluster and verify that it will fail
        """

        plugin.prepare_contrail_plugin(self, slaves=3)

        # enable plugin in contrail settings
        plugin.activate_plugin(self)

        self.fuel_web.update_nodes(
            self.cluster_id,
            {
                'slave-01': ['controller'],
                'slave-02': ['compute'],
                'slave-03': ['contrail-config']
            })

        openstack.deploy_cluster(self, wait_for_status='error')
        cluster_info = self.fuel_web.client.get_cluster(self.cluster_id)
        assert_equal(cluster_info['status'], 'error'), "Error was expected"

    @test(depends_on=[SetupEnvironment.prepare_slaves_3],
          groups=["cannot_deploy_only_contrail_control"])
    @log_snapshot_after_test
    def cannot_deploy_only_contrail_control(self):
        """Check can not deploy Contrail cluster with "contrail_control" only

        Scenario:
            1. Create an environment with
               "Neutron with tunneling segmentation"
               as a network configuration
            2. Enable and configure Contrail plugin
            3. Add 1 node with "Controller" and 1 node with "Compute" role
            4. Add 1 nodes with "contrail-control" role
            5. Deploy cluster and verify that it will fail
        """

        plugin.prepare_contrail_plugin(self, slaves=3)

        # enable plugin in contrail settings
        plugin.activate_plugin(self)

        self.fuel_web.update_nodes(
            self.cluster_id,
            {
                'slave-01': ['controller'],
                'slave-02': ['compute'],
                'slave-03': ['contrail-control']
            })

        openstack.deploy_cluster(self, wait_for_status='error')
        cluster_info = self.fuel_web.client.get_cluster(self.cluster_id)
        assert_equal(cluster_info['status'], 'error'), "Error was expected"

    @test(depends_on=[SetupEnvironment.prepare_slaves_5],
          groups=["contrail_ha_with_node_problems"])
    @log_snapshot_after_test
    def contrail_ha_with_node_problems(self):
        """ Check Contrail HA using node problems
            1. Deploy cluster in the following node configuration:
                node-01: 'contrail-config'
                node-02: 'contrail-control'
                node-03: 'contrail-db'
                node-04: 'controller'
                node-05: 'compute'
            2. Login as admin to Openstack Horizon UI
            3. Launch 2 new instances
            4. Run smoke test set to check connectivity
            5. With a pause of 5 minutes turn off and turn on
               each of Contrail Nodes
            6. Run smoke test set to check connectivity
        """
        plugin.prepare_contrail_plugin(self, slaves=5)

        # enable plugin in contrail settings
        plugin.activate_plugin(self)

        contrail_node_conf = {
            'slave-01': ['contrail-config'],
            'slave-02': ['contrail-control'],
            'slave-03': ['contrail-db'],
        }
        os_node_conf = {
            'slave-04': ['controller'],
            'slave-05': ['compute'],
        }

        self.fuel_web.update_nodes(self.cluster_id,
                                   dict(contrail_node_conf, **os_node_conf))
        openstack.deploy_cluster(self)

        def get_cluster_node(node_name):
            # Shutdown contrail node
            for node in self.fuel_web.client.list_cluster_nodes(self.cluster_id):
                if node_name in node['name']:
                    return self.fuel_web.get_devops_nodes_by_nailgun_nodes([cluster_node])
            else:
                return None

        for conf_node_name, roles in contrail_node_conf.items():
            cluster_node = get_cluster_node()
            assert_is_none(cluster_node,
                           'Cluster node "%s" not found' % conf_node_name)
            logger.info('Shutdown node "%s"' % conf_node_name)

            # Shutdown node
            self.fuel_web.warm_shutdown_nodes([cluster_node])

            time.sleep(60*5)  # Sleep for 5 minutes

            # Check connectivity
            self.fuel_web.run_ostf(cluster_id=self.cluster_id,
                                   test_sets=['smoke'])

            # Start node back
            self.fuel_web.warm_start_nodes([cluster_node])

            # Check connectivity again
            self.fuel_web.run_ostf(cluster_id=self.cluster_id,
                                   test_sets=['smoke'])

    @test(depends_on=[SetupEnvironment.prepare_slaves_5],
          groups=["contrail_ha_with_node_problems"])
    @log_snapshot_after_test
    def contrail_ha_with_node_problems(self):
        """ Check Contrail HA using node problems
            1. Deploy cluster in the following node configuration:
                node-01: 'contrail-config'
                node-02: 'contrail-control'
                node-03: 'contrail-db'
                node-04: 'controller'
                node-05: 'compute'
            2. Login as admin to Openstack Horizon UI
            3. Launch 2 new instances
            4. Run smoke test set to check connectivity
            5. With a pause of 5 minutes stop and start
               private and management interface on contrail-control node
            6. Run smoke test set to check connectivity
        """
        plugin.prepare_contrail_plugin(self, slaves=5)

        # enable plugin in contrail settings
        plugin.activate_plugin(self)

        os_node_conf = {
            'slave-01': ['contrail-config'],
            'slave-03': ['contrail-db'],
            'slave-04': ['controller'],
            'slave-05': ['compute'],
        }

        contrail_controller = {
            'slave-02': ['contrail-control'],
        }

        self.fuel_web.update_nodes(self.cluster_id,
                                   dict(contrail_controller, **os_node_conf))
        openstack.deploy_cluster(self)

        def get_cluster_node(node_name):
            # Shutdown contrail node
            for node in self.fuel_web.client.list_cluster_nodes(self.cluster_id):
                if node_name in node['name']:
                    return self.fuel_web.get_devops_nodes_by_nailgun_nodes([cluster_node])
            else:
                return None

        for conf_node_name, roles in contrail_controller.items():
            cluster_node = get_cluster_node()
            assert_is_none(cluster_node,
                           'Cluster node "%s" not found' % conf_node_name)
            logger.info('Shutdown node "%s"' % conf_node_name)

            # Stop private and management interfaces
            # FIXME: Stop private and management interfaces

            time.sleep(60*5)  # Sleep for 5 minutes

            # Check connectivity
            self.fuel_web.run_ostf(cluster_id=self.cluster_id,
                                   test_sets=['smoke'])

            # Stop private and management interfaces
            # FIXME: Resume private and management interfaces

            # Check connectivity again
            self.fuel_web.run_ostf(cluster_id=self.cluster_id,
                                   test_sets=['smoke'])
