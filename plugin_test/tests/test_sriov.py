"""Copyright 2016 Mirantis, Inc.

Licensed under the Apache License, Version 2.0 (the "License"); you may
not use this file except in compliance with the License. You may obtain
a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
License for the specific language governing permissions and limitations
under the License.
"""

import os
from proboscis import test
from fuelweb_test.helpers.decorators import log_snapshot_after_test
from fuelweb_test.settings import CONTRAIL_PLUGIN_PACK_UB_PATH
from fuelweb_test.tests.base_test_case import SetupEnvironment
from fuelweb_test.tests.base_test_case import TestBasic
from helpers import plugin
from helpers import openstack
from helpers import baremetal


@test(groups=["plugins"])
class SRIOVTests(TestBasic):
    """DPDKTests."""

    pack_copy_path = '/var/www/nailgun/plugins/contrail-4.0'
    add_package = '/var/www/nailgun/plugins/contrail-4.0/'\
                  'repositories/ubuntu/contrail-setup*'
    ostf_msg = 'OSTF tests passed successfully.'
    cluster_id = ''
    pack_path = CONTRAIL_PLUGIN_PACK_UB_PATH
    CONTRAIL_DISTRIBUTION = os.environ.get('CONTRAIL_DISTRIBUTION')
    bm_drv = baremetal.BMDriver()

    @test(depends_on=[SetupEnvironment.prepare_slaves_9],
          groups=["contrail_ha_sriov"])
    @log_snapshot_after_test
    def contrail_ha_sriov(self):
        """Check Contrail deploy on HA environment.

        Scenario:
            1. Create an environment with "Neutron with tunneling
               segmentation" as a network configuration and CEPH storage
            2. Enable and configure Contrail plugin
            3. Deploy cluster with following node configuration:
                node-01: 'controller';
                node-02: 'controller';
                node-03: 'controller', 'ceph-osd';
                node-04: 'compute', 'ceph-osd';
                node-05: 'compute', 'ceph-osd';
                node-07: 'contrail-db';
                node-08: 'contrail-config';
                node-09: 'contrail-control';
                node-sriov: 'compute', sriov';
            4. Run OSTF tests

        Duration 120 min

        """
        self.show_step(1)
        plugin.prepare_contrail_plugin(self, slaves=9,
                                       options={'images_ceph': True,
                                                'volumes_ceph': True,
                                                'ephemeral_ceph': True,
                                                'objects_ceph': True,
                                                'volumes_lvm': False})
        self.bm_drv.host_prepare()

        self.show_step(2)
        # enable plugin and ativate SR-IOV in contrail settings
        plugin.activate_sriov(self)
        # activate vSRX image
        vsrx_setup_result = plugin.activate_vsrx()

        plugin.show_range(self, 3, 4)
        self.bm_drv.setup_fuel_node(self,
                                    cluster_id=self.cluster_id,
                                    roles=['compute', 'sriov'])

        conf_nodes = {
            'slave-01': ['controller'],
            'slave-02': ['controller'],
            'slave-03': ['controller', 'ceph-osd'],
            'slave-04': ['compute', 'ceph-osd'],
            'slave-05': ['compute', 'ceph-osd'],
            'slave-06': ['contrail-db'],
            'slave-07': ['contrail-config'],
            'slave-08': ['contrail-control'],
        }
        # Cluster configuration
        self.fuel_web.update_nodes(self.cluster_id,
                                   nodes_dict=conf_nodes,
                                   update_interfaces=False)
        self.bm_drv.update_vm_node_interfaces(self, self.cluster_id)
        # Deploy cluster
        openstack.deploy_cluster(self)
        # Run OSTF tests
        if vsrx_setup_result:
            self.fuel_web.run_ostf(cluster_id=self.cluster_id,
                                   test_sets=['smoke', 'sanity', 'ha'],
                                   should_fail=1,
                                   failed_test_name=['Instance live migration'])
