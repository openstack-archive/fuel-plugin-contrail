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
import os.path

from proboscis import test
from proboscis.asserts import assert_equal
from proboscis.asserts import assert_true

from fuelweb_test.helpers.decorators import log_snapshot_after_test
from fuelweb_test.settings import CONTRAIL_PLUGIN_PACK_UB_PATH
from fuelweb_test.tests.base_test_case import SetupEnvironment
from fuelweb_test.tests.base_test_case import TestBasic

from helpers import openstack
from helpers import plugin
from helpers import vsrx
from helpers.settings import CONTRAIL_PLUGIN_VERSION
from helpers.settings import OSTF_RUN_TIMEOUT
from tests.test_contrail_check import TestContrailCheck


@test(groups=["plugins"])
class ContrailPlugin(TestBasic):
    """ContrailPlugin."""  # TODO(unknown) documentation

    pack_copy_path = '/var/www/nailgun/plugins/contrail-5.0'
    add_package = \
        '/var/www/nailgun/plugins/contrail-5.0/' \
        'repositories/ubuntu/contrail-setup*'
    ostf_msg = 'OSTF tests passed successfully.'

    cluster_id = ''

    pack_path = CONTRAIL_PLUGIN_PACK_UB_PATH

    CONTRAIL_DISTRIBUTION = os.environ.get('CONTRAIL_DISTRIBUTION')

    @test(depends_on=[SetupEnvironment.prepare_slaves_3],
          groups=["install_contrail"])
    @log_snapshot_after_test
    def install_contrail(self):
        """Install Contrail Plugin and create cluster.

        Scenario:
            1. Upload a plugin to Fuel Master node using scp.
            2. Connect to Fuel Master node via ssh.
            3. Install plugin with fuel-cli.
            4. Connect to Fuel web UI.
            5. Click on the "Create Environment" button.
            6. Configure Environment with the "Neutron with tunneling
               segmentation" network configuration.
            7. Activate plugin and all checkboxes.
            8. Verify that Contrail Plugin Configure Checkboxes are present
               and active. Check default vaules.

        Duration 20 min

        """
        # defaults
        plugin_name = 'contrail'
        contrail_api_port = '8082'
        contrail_route_target = '10000'
        contrail_external = '10.100.1.0/24'
        contrail_asnum = '64512'
        vrouter_core_mask = '0xf'

        plugin.show_range(self, 1, 7)
        plugin.prepare_contrail_plugin(self, slaves=3)

        cluster_id = self.fuel_web.get_last_created_cluster()
        cmd = 'fuel plugins list'

        output = list(self.env.d_env.get_admin_remote().execute(
            cmd)['stdout']).pop().split(' ')

        # check name
        assert_true(
            plugin_name in output,
            "Plugin  {} is not installed.".format(plugin_name)
        )
        # check version
        assert_true(
            CONTRAIL_PLUGIN_VERSION in output,
            "Plugin  {} is not installed.".format(CONTRAIL_PLUGIN_VERSION)
        )

        self.show_step(7)
        plugin.activate_plugin(
            self, contrail_global_dpdk=True, dpdk_on_vf=True)

        self.show_step(8)
        attr = self.fuel_web.client.get_cluster_attributes(
            cluster_id)['editable'][plugin_name]['metadata']

        state = attr['enabled']
        assert_equal(state, True, "Plugin is not enabled.")

        attr = attr['versions'][0]
        vers = attr['metadata']['plugin_version']
        assert_equal(
            CONTRAIL_PLUGIN_VERSION, vers,
            "Invalid version.".format(vers))

        assert_equal(
            contrail_api_port, attr['contrail_api_public_port']['value'],
            "Invalid  contrail api port {0}.".format(
                attr['contrail_api_public_port']['value']))

        assert_equal(
            True, attr['dpdk_on_vf']['value'],
            "Dpdk on vf is disabled.")

        assert_equal(
            contrail_route_target, attr['contrail_route_target']['value'],
            "Invalid default contrail route target {0}.".format(
                attr['contrail_route_target']['value']))

        assert_equal(
            True, attr['contrail_global_dpdk']['value'],
            "Contrail global dpdk is disabled.")

        assert_equal(
            True, attr['patch_nova']['value'],
            "Patch_nova is not enabled by default.")

        assert_equal(
            vrouter_core_mask, attr['vrouter_core_mask']['value'],
            "Invalid default vrouter_core_mask {0}.".format(
                attr['vrouter_core_mask']['value']))

        assert_equal(
            contrail_asnum, attr['contrail_asnum']['value'],
            "Invalid default sriov physnet {0}.".format(
                attr['contrail_asnum']['value']))

        assert_equal(
            contrail_external, attr['contrail_external']['value'],
            "Invalid default 'contrail external' {0}.".format(
                attr['contrail_external']['value']))

    @test(depends_on=[SetupEnvironment.prepare_slaves_5],
          groups=["contrail_smoke"])
    @log_snapshot_after_test
    def contrail_smoke(self):
        """Deploy a cluster with Contrail Plugin.

        Scenario:
            1. Create an environment with "Neutron with tunneling
               segmentation" as a network configuration
            2. Enable Contrail plugin
            3. Add a node with contrail-controller
            4. Add a node with contrail-analytics and
               contrail-analytics-db roles
            4. Add a node with controller role
            5. Add a node with compute role
            6. Deploy cluster with plugin
            7. Update plugin

        Duration 90 min

        """
        self.show_step(1)
        plugin.prepare_contrail_plugin(self, slaves=5)

        self.show_step(2)
        plugin.activate_plugin(self)

        plugin.show_range(self, 3, 6)
        self.fuel_web.update_nodes(
            self.cluster_id,
            {
                'slave-01': ['contrail-controller'],
                'slave-02': ['contrail-analytics', 'contrail-analytics-db'],
                'slave-03': ['controller'],
                'slave-04': ['compute'],
            })

        self.show_step(6)
        openstack.deploy_cluster(self)
        TestContrailCheck(self).cloud_check(['contrail'])
        self.show_step(7)
        plugin.update_plugin(self)

    @test(depends_on=[SetupEnvironment.prepare_slaves_9],
          groups=["contrail_bvt"])
    @log_snapshot_after_test
    def contrail_bvt(self):
        """BVT test for contrail plugin.

        Deploy cluster with 1 controller, 1 compute,
        3 contrail-config, contrail-control, contrail-db roles
        and install contrail plugin

        Scenario:
            1. Create an environment with "Neutron with tunneling
               segmentation" as a network configuration
            2. Enable Contrail plugin
            3. Add 2 nodes with contrail-controller role
            4. Add 2 nodes with contrail-analytics-db role.
            5. Add a node with contrail-analytics + contrail-analytics-db roles
            6. Add a node with contrail-analytics + contrail-controller roles
            7. Add a node with contrail-analytics role
            8. Add a node with with controller role
            9. Add a node with compute + cinder role
            10. Deploy cluster with plugin
            11. Run contrail health check tests
            12. Run OSTF tests

        Duration 110 min

        """
        self.show_step(1)
        plugin.prepare_contrail_plugin(self, slaves=9)

        self.show_step(2)
        plugin.activate_plugin(self)
        # activate vSRX image
        vsrx_setup_result = vsrx.activate()

        plugin.show_range(self, 3, 10)
        self.fuel_web.update_nodes(
            self.cluster_id,
            {
                'slave-01': ['contrail-controller'],
                'slave-02': ['contrail-controller'],
                'slave-03': ['contrail-controller',
                            'contrail-analytics'],
                'slave-04': ['contrail-analytics-db',
                            'contrail-analytics'],
                'slave-05': ['contrail-analytics-db'],
                'slave-06': ['contrail-analytics-db'],
                'slave-07': ['contrail-analytics'],
                'slave-08': ['controller'],
                'slave-09': ['compute', 'cinder']
            })

        self.show_step(10)
        openstack.deploy_cluster(self)

        self.show_step(11)
        TestContrailCheck(self).cloud_check(['contrail'])

        self.show_step(12)
        if vsrx_setup_result:
            self.fuel_web.run_ostf(cluster_id=self.cluster_id,
                                   timeout=OSTF_RUN_TIMEOUT)
