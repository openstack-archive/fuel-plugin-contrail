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
from proboscis.asserts import assert_equal
from proboscis import test
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

        self.show_step(1)
        plugin.prepare_contrail_plugin(self, slaves=3)

        self.show_step(2)
        plugin.activate_plugin(self)

        plugin.show_range(3, 5)
        self.fuel_web.update_nodes(
            self.cluster_id,
            {
                'slave-01': ['controller'],
                'slave-02': ['compute'],
                'slave-03': ['contrail-db']
            })

        self.show_step(5)
        task = self.fuel_web.deploy_cluster(self.cluster_id)
        self.fuel_web.assert_task_failed(task, timeout=130 * 60, interval=30)

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

        self.show_step(1)
        plugin.prepare_contrail_plugin(self, slaves=3)

        self.show_step(2)
        plugin.activate_plugin(self)

        plugin.show_range(3, 5)
        self.fuel_web.update_nodes(
            self.cluster_id,
            {
                'slave-01': ['controller'],
                'slave-02': ['compute'],
                'slave-03': ['contrail-config']
            })

        self.show_step(5)
        task = self.fuel_web.deploy_cluster(self.cluster_id)
        self.fuel_web.assert_task_failed(task, timeout=130 * 60, interval=30)

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

        self.show_step(1)
        plugin.prepare_contrail_plugin(self, slaves=3)

        self.show_step(2)
        plugin.activate_plugin(self)

        plugin.show_range(3, 5)
        self.fuel_web.update_nodes(
            self.cluster_id,
            {
                'slave-01': ['controller'],
                'slave-02': ['compute'],
                'slave-03': ['contrail-control']
            })

        self.show_step(5)
        task = self.fuel_web.deploy_cluster(self.cluster_id)
        self.fuel_web.assert_task_failed(task, timeout=130 * 60, interval=30)

