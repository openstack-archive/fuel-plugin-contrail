#    Copyright 2015 Mirantis, Inc.
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
import os.path
import time
from proboscis import test
from fuelweb_test.helpers.decorators import log_snapshot_after_test
from fuelweb_test.settings import CONTRAIL_PLUGIN_PACK_UB_PATH
from fuelweb_test.tests.base_test_case import SetupEnvironment
from fuelweb_test.tests.base_test_case import TestBasic
from helpers import plugin
from helpers import openstack


@test(groups=["plugins"])
class ContrailPlugin(TestBasic):
    """ContrailPlugin."""  # TODO documentation

    pack_copy_path = '/var/www/nailgun/plugins/contrail-3.0'
    add_package = \
        '/var/www/nailgun/plugins/contrail-3.0/' \
        'repositories/ubuntu/contrail-setup*'
    ostf_msg = 'OSTF tests passed successfully.'

    cluster_id = ''

    pack_path = CONTRAIL_PLUGIN_PACK_UB_PATH

    CONTRAIL_DISTRIBUTION = os.environ.get('CONTRAIL_DISTRIBUTION')

    @test(depends_on=[SetupEnvironment.prepare_slaves_3],
          groups=["install_contrail"])
    @log_snapshot_after_test
    def install_contrail(self):
        """Install Contrail Plugin and create cluster

        Scenario:
            1. Revert snapshot "ready_with_5_slaves"
            2. Upload contrail plugin to the master node
            3. Install plugin and additional packages
            4. Enable Neutron with tunneling segmentation
            5. Create cluster

        Duration 20 min

        """

        plugin.prepare_contrail_plugin(self, slaves=3)

    @test(depends_on=[SetupEnvironment.prepare_slaves_3],
          groups=["contrail_smoke"])
    @log_snapshot_after_test
    def contrail_smoke(self):
        """Deploy a cluster with Contrail Plugin

        Scenario:
            1. Revert snapshot "ready_with_3_slaves"
            2. Create cluster
            3. Add 1 node with contrail-config, contrail-control and
               contrail-db roles
            4. Add a node with controller role
            4. Add a node with compute role
            6. Enable Contrail plugin
            5. Deploy cluster with plugin

        Duration 90 min

        """
        plugin.prepare_contrail_plugin(self, slaves=3)

        # enable plugin in contrail settings
        plugin.activate_plugin(self)

        self.fuel_web.update_nodes(
            self.cluster_id,
            {
                'slave-01': ['contrail-config',
                             'contrail-control',
                             'contrail-db'],
                'slave-02': ['controller'],
                'slave-03': ['compute'],
            })

        # deploy cluster
        openstack.deploy_cluster(self)

    @test(depends_on=[SetupEnvironment.prepare_slaves_9],
          groups=["contrail_bvt"])
    @log_snapshot_after_test
    def contrail_bvt(self):
        """BVT test for contrail plugin
        Deploy cluster with 1 controller, 1 compute,
        3 contrail-config, contrail-control, contrail-db roles
        and install contrail plugin

        Scenario:
            1. Revert snapshot "ready_with_9_slaves"
            2. Create cluster
            3. Add 3 nodes with contrail-db role
            4. Add a node with contrail-config role
            5. Add a node with contrail-control role
            6. Add a node with with controller role
            7. Add a node with compute + cinder role
            8. Enable Contrail plugin
            9. Deploy cluster with plugin
            10. Create net and subnet
            11. Run OSTF tests

        Duration 110 min

        """
        plugin.prepare_contrail_plugin(self, slaves=9)

        # enable plugin in contrail settings
        plugin.activate_plugin(self)
        # activate vSRX image
        vsrx_setup_result = plugin.activate_vsrx()

        self.fuel_web.update_nodes(
            self.cluster_id,
            {
                'slave-01': ['contrail-config'],
                'slave-02': ['contrail-control'],
                'slave-03': ['contrail-db'],
                'slave-04': ['contrail-db'],
                'slave-05': ['contrail-db'],
                'slave-06': ['controller'],
                'slave-07': ['compute', 'cinder'],
            })

        # deploy cluster
        openstack.deploy_cluster(self)

        # FIXME: remove next line when bug #1516969 will be fixed
        time.sleep(60*25)

        if vsrx_setup_result:
            self.fuel_web.run_ostf(cluster_id=self.cluster_id)
