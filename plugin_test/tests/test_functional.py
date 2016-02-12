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
from proboscis import test
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
