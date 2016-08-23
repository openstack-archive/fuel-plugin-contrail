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
from helpers import vsrx
from helpers import plugin
from helpers import openstack
from helpers import baremetal
from tests.test_contrail_check import TestContrailCheck


@test(groups=["plugins"])
class DPDKVFTests(TestBasic):
    """DPDK VF Tests."""

    pack_copy_path = '/var/www/nailgun/plugins/contrail-4.0'
    add_package = '/var/www/nailgun/plugins/contrail-4.0/'\
                  'repositories/ubuntu/contrail-setup*'
    ostf_msg = 'OSTF tests passed successfully.'
    cluster_id = ''
    pack_path = CONTRAIL_PLUGIN_PACK_UB_PATH
    CONTRAIL_DISTRIBUTION = os.environ.get('CONTRAIL_DISTRIBUTION')
    bm_drv = baremetal.BMDriver()

    @test(depends_on=[SetupEnvironment.prepare_slaves_9],
          groups=["contrail_ha_dpdk_vf"])
    @log_snapshot_after_test
    def contrail_ha_dpdk_vf(self):
        """Check Contrail deploy on HA environment.

        Scenario:
            1. Create an environment with "Neutron with tunneling segmentation"
                as a network configuration and CEPH storage
            2. Enable and configure Contrail plugin:
                * enable dpdk
                * enable sriov
                * enable DPDK on VF
            3. Add following nodes:
                * 3 controller + mongo
                * 3 compute + ceph
                * 1 contrail-config+contrail-control+contrail-db
                * 1 compute+sriov+dpdk
                * 1 contrail-db+contrail-analytics
                * 1 contrail-db
            4. Deploy cluster.
            5. Run OSTF tests.
            6. Run contrail health check tests

        Duration 120 min

        """
        self.show_step(1)
        plugin.prepare_contrail_plugin(self, slaves=9,
                                       options={'images_ceph': True,
                                                'volumes_ceph': True,
                                                'ephemeral_ceph': True,
                                                'objects_ceph': True,
                                                'ceilometer': True,
                                                'volumes_lvm': False})
        self.bm_drv.host_prepare()

        self.show_step(2)
        # enable plugin in contrail settings
        plugin.activate_plugin(self)
        # activate DPDK feature
        plugin.activate_dpdk_vf(self)
        # activate vSRX image
        vsrx_setup_result = vsrx.activate()

        self.show_step(3)
        self.bm_drv.setup_fuel_node(self,
                                    cluster_id=self.cluster_id,
                                    roles=['compute', 'dpdk', 'sriov'])

        conf_nodes = {
            'slave-01': ['controller', 'mongo'],
            'slave-02': ['controller', 'mongo'],
            'slave-03': ['controller', 'mongo'],
            'slave-04': ['compute', 'ceph-osd'],
            'slave-05': ['compute', 'ceph-osd'],
            'slave-06': ['compute', 'ceph-osd'],
            'slave-07': ['contrail-db', 'contrail-config', 'contrail-control'],
            'slave-08': ['contrail-db', 'contrail-analytics'],
            'slave-09': ['contrail-db'],
        }
        # Cluster configuration
        self.fuel_web.update_nodes(self.cluster_id,
                                   nodes_dict=conf_nodes,
                                   update_interfaces=False)
        self.bm_drv.update_vm_node_interfaces(self, self.cluster_id)
        # Deploy cluster
        self.show_step(4)
        openstack.deploy_cluster(self)
        # Run OSTF tests
        # FIXME: remove shouldfail, when livemigration+DPDK works
        if vsrx_setup_result:
            self.show_step(5)
            self.fuel_web.run_ostf(cluster_id=self.cluster_id,
                                   test_sets=['smoke', 'sanity',
                                              'ha', 'tests_platform'],
                                   timeout=60 * 60,
                                   should_fail=1,
                                   failed_test_name=['Instance live migration']
                                   )
            self.show_step(6)
            TestContrailCheck(self).cloud_check(
                ['dpdk', 'contrail'],
                should_fail=[
                    'test_dpdk_check_public_connectivity_from_instance'
                ]
            )
