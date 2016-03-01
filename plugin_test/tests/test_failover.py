# coding=utf-8
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
from proboscis.asserts import assert_false
from proboscis.asserts import assert_true
from proboscis import test
from fuelweb_test.helpers.decorators import log_snapshot_after_test
from fuelweb_test.settings import CONTRAIL_PLUGIN_PACK_UB_PATH
from fuelweb_test.tests.base_test_case import SetupEnvironment
from fuelweb_test.tests.base_test_case import TestBasic
from fuelweb_test.models.nailgun_client import NailgunClient
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

    def cannot_uninstall_plugin_with_deployed_env(self):
        """Check cannot uninstall Contrail plugin, which is enable for environment

        Scenario:
            1. Try to remove plugin and ensure that alert presents
               in cli: “400 Client Error: Bad Request (Can not delete
               plugin which is enabled for some environment.)”
            2. Remove environment
            3. Remove plugin
            5. Check that it was removed successfully

        """
        # Try to remove plugin
        plugin_name = "contrail"
        plugin_version = os.environ.get('CONTRAIL_PLUGIN_PATH').split('-')[2]
        expected_msg = '400 Client Error: Bad Request (Can\'t delete plugin which is enabled for some environment.)'

        self.env.revert_snapshot("snapshot_for_test")

        cmd = 'fuel plugins --remove {0}=={1}'.format(plugin_name,plugin_version)

        msg = self.env.d_env.get_admin_remote().execute(cmd)['stdout']

        # check alert in cli
        assert_equal(msg, expected_msg), "Error: Wrong alert in cli"

        # check plugin`s list
        output = list(self.env.d_env.get_admin_remote().execute('fuel plugins list')['stdout'])

        assert_false (plugin_name in output[-1],"Failed: Plugin has removed")

        # remove environment
        cluster_id = NailgunClient.list_clusters[0]['id']

        NailgunClient.delete_cluster(cluster_id)

        # remove plugin and verify it
        self.env.d_env.get_admin_remote().execute(cmd)

        output = list(self.env.d_env.get_admin_remote().execute('fuel plugins list')['stdout'])

        assert_true (plugin_name in output[-1],"Failed: Plugin hasn`t removed")

