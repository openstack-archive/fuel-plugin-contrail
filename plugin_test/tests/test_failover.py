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
from proboscis.asserts import assert_true
from fuelweb_test.helpers.decorators import log_snapshot_after_test
from fuelweb_test.settings import CONTRAIL_PLUGIN_PACK_UB_PATH
from fuelweb_test.tests.base_test_case import SetupEnvironment
from fuelweb_test.tests.base_test_case import TestBasic
from helpers import plugin
from helpers.settings import CONTRAIL_PLUGIN_VERSION


@test(groups=["plugins"])
class FailoverTests(TestBasic):
    """FailoverTests."""

    pack_copy_path = '/var/www/nailgun/plugins/contrail-4.0'
    add_package = '/var/www/nailgun/plugins/contrail-4.0/'\
                  'repositories/ubuntu/contrail-setup*'
    ostf_msg = 'OSTF tests passed successfully.'
    cluster_id = ''
    pack_path = CONTRAIL_PLUGIN_PACK_UB_PATH
    CONTRAIL_DISTRIBUTION = os.environ.get('CONTRAIL_DISTRIBUTION')

    @test(depends_on=[SetupEnvironment.prepare_slaves_3],
          groups=["cannot_deploy_only_contrail_db"])
    @log_snapshot_after_test
    def cannot_deploy_only_contrail_db(self):
        """Check can not deploy Contrail cluster with "contrail_db" only.

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

        plugin.show_range(self, 3, 5)
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
        """Check can not deploy Contrail cluster with "contrail_config" only.

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

        plugin.show_range(self, 3, 5)
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
        """Check can not deploy Contrail cluster with "contrail_control" only.

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

        plugin.show_range(self, 3, 5)
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

    @test(depends_on=[SetupEnvironment.prepare_slaves_3],
          groups=["contrail_uninstall"])
    @log_snapshot_after_test
    def contrail_uninstall(self):
        """Check that plugin can be removed.

        Scenario:
            1. Install plugin and create cluster with activated plugin.
            2. Try to remove plugin and ensure that alert presents in cli:
               '400 Client Error: Bad Request (Can not delete plugin which
               is enabled for some environment.)'
            3. Remove environment.
            4. Remove plugin.
            5. Check that it was removed successfully.


        Duration: 5 min

        """
        # constants
        plugin_name = 'contrail'
        message = "400 Client Error: Bad Request (Can't delete plugin" + \
            " which is enabled for some environment.)"

        self.show_step(1)
        plugin.prepare_contrail_plugin(self, slaves=3)
        plugin.activate_plugin(self)
        cluster_id = self.fuel_web.get_last_created_cluster()

        self.show_step(2)
        cmd = 'fuel plugins --remove {0}=={1}'.format(
            plugin_name, CONTRAIL_PLUGIN_VERSION)

        result = self.env.d_env.get_admin_remote().execute(cmd)
        assert_true(
            result['exit_code'] == 1,
            'Plugin is removed.')

        assert_true(
            result['stderr'].pop().splitlines().pop() == message,
            'Error message was not displayed.')

        self.show_step(3)
        self.fuel_web.delete_env_wait(cluster_id)

        self.show_step(4)
        result = self.env.d_env.get_admin_remote().execute(cmd)
        assert_true(
            result['exit_code'] == 0,
            'Plugin was not removed.')

        self.show_step(5)
        cmd = 'fuel plugins list'
        output = list(self.env.d_env.get_admin_remote().execute(
            cmd)['stdout']).pop().split(' ')

        assert_true(
            plugin_name not in output,
            "Plugin is not removed {}".format(plugin_name)
        )
