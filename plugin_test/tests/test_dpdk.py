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
class DPDKTests(TestBasic):
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
          groups=["contrail_ha_dpdk"])
    @log_snapshot_after_test
    def contrail_ha_dpdk(self):
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
                node-dpdk: 'compute', dpdk';
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
        # enable plugin in contrail settings
        plugin.activate_plugin(self)
        # activate DPDK feature
        plugin.activate_dpdk(self)
        # activate vSRX image
        vsrx_setup_result = plugin.activate_vsrx()

        plugin.show_range(self, 3, 4)
        self.bm_drv.setup_fuel_node(self,
                                    cluster_id=self.cluster_id,
                                    roles=['compute', 'dpdk'])

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
                                   test_sets=['smoke', 'sanity', 'ha'])

    @test(depends_on=[SetupEnvironment.prepare_slaves_9],
          groups=["contrail_dpdk_add_compute"])
    @log_snapshot_after_test
    def contrail_dpdk_add_compute(self):
        """Verify that Contrail compute role can be added after deploying.

        Scenario:
            1. Create an environment with "Neutron with tunneling
               segmentation" as a network configuration
            2. Enable and configure Contrail plugin
            3. Deploy cluster with following node configuration:
                node-1: 'controller', 'ceph-osd';
                node-2: 'contrail-config', 'contrail-control', 'contrail-db';
                node-3: 'contrail-db';
                node-4: 'compute', 'dpdk';
                node-5: 'compute', 'ceph-osd';
            4. Run OSTF tests
            5. Check Controller and Contrail nodes status
            6. Add one node with following configuration:
                node-6: "compute", "ceph-osd";
            7. Deploy changes
            8. Run OSTF tests

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
        # enable plugin in contrail settings
        plugin.activate_plugin(self)
        # activate DPDK feature
        plugin.activate_dpdk(self)
        # activate vSRX image
        vsrx_setup_result = plugin.activate_vsrx()

        plugin.show_range(self, 3, 5)
        self.bm_drv.setup_fuel_node(self,
                                    cluster_id=self.cluster_id,
                                    roles=['compute', 'ceph-osd', 'dpdk'])
        conf_nodes = {
            'slave-01': ['controller', 'ceph-osd'],
            'slave-02': ['contrail-config',
                         'contrail-control',
                         'contrail-db'],
            'slave-03': ['contrail-db'],
            'slave-04': ['compute', 'ceph-osd'],
            'slave-05': ['compute', 'ceph-osd'],
        }
        conf_compute = {'slave-06': ['compute']}

        # Cluster configuration
        self.fuel_web.update_nodes(self.cluster_id,
                                   nodes_dict=conf_nodes,
                                   update_interfaces=False)
        self.bm_drv.update_vm_node_interfaces(self, self.cluster_id)
        # Deploy cluster
        openstack.deploy_cluster(self)
        # Run OSTF tests
        if vsrx_setup_result:
            self.fuel_web.run_ostf(cluster_id=self.cluster_id)

        # Add Compute node and check again
        plugin.show_range(self, 6, 8)
        openstack.update_deploy_check(self, conf_compute,
                                      is_vsrx=vsrx_setup_result)
        # Cluster configuration
        self.fuel_web.update_nodes(self.cluster_id,
                                   nodes_dict=conf_compute,
                                   update_interfaces=False)
        self.bm_drv.update_vm_node_interfaces(self, self.cluster_id)
        # Deploy cluster
        openstack.deploy_cluster(self)
        # Run OSTF tests
        if vsrx_setup_result:
            self.fuel_web.run_ostf(cluster_id=self.cluster_id)

    @test(depends_on=[SetupEnvironment.prepare_slaves_9],
          groups=["contrail_dpdk_delete_compute"])
    @log_snapshot_after_test
    def contrail_dpdk_delete_compute(self):
        """Verify that Contrail compute role can be deleted after deploying.

        Scenario:
            1. Create an environment with "Neutron with tunneling
               segmentation" as a network configuration
            2. Enable and configure Contrail plugin
            3. Deploy cluster with following node configuration:
                node-01: 'controller';
                node-02: 'contrail-control', 'contrail-config', 'contrail-db';
                node-03: 'contrail-db';
                node-04: 'compute', 'cinder', 'dpdk';
                node-05: 'compute', 'cinder';
                node-06: 'compute';
            4. Run OSTF tests
            5. Delete node-06 with "compute" role
            6. Deploy changes
            7. Run OSTF tests

        """
        self.show_step(1)
        plugin.prepare_contrail_plugin(self, slaves=9)
        self.bm_drv.host_prepare()

        self.show_step(2)
        # enable plugin in contrail settings
        plugin.activate_plugin(self)
        # activate DPDK feature
        plugin.activate_dpdk(self)
        # activate vSRX image
        vsrx_setup_result = plugin.activate_vsrx()

        plugin.show_range(self, 3, 4)
        self.bm_drv.setup_fuel_node(self,
                                    cluster_id=self.cluster_id,
                                    roles=['compute', 'cinder', 'dpdk'])
        conf_no_compute = {
            'slave-01': ['controller'],
            'slave-02': ['contrail-control',
                         'contrail-config',
                         'contrail-db'],
            'slave-03': ['contrail-db'],
            'slave-04': ['compute', 'cinder'],
        }
        conf_compute = {'slave-05': ['compute']}

        self.fuel_web.update_nodes(
            self.cluster_id,
            nodes_dict=dict(conf_no_compute, **conf_compute),
            update_interfaces=False)
        self.bm_drv.update_vm_node_interfaces(self, self.cluster_id)
        # Deploy cluster
        openstack.deploy_cluster(self)
        # Run OSTF tests
        if vsrx_setup_result:
            self.fuel_web.run_ostf(cluster_id=self.cluster_id)

        # Delete Compute node and check again
        plugin.show_range(self, 5, 7)
        self.fuel_web.update_nodes(
            self.cluster_id,
            nodes_dict=conf_compute,
            pending_addition=False, pending_deletion=True,
            update_interfaces=False)
        self.bm_drv.update_vm_node_interfaces(self, self.cluster_id)
        # Deploy cluster
        openstack.deploy_cluster(self)
        # Run OSTF tests
        if vsrx_setup_result:
            self.fuel_web.run_ostf(cluster_id=self.cluster_id,
                                   test_sets=['smoke', 'sanity'],
                                   should_fail=1,
                                   failed_test_name=['Check that required '
                                                     'services are running']
                                   )

    @test(depends_on=[SetupEnvironment.prepare_slaves_9],
          groups=["contrail_dpdk_add_dpdk"])
    @log_snapshot_after_test
    def contrail_dpdk_add_dpdk(self):
        """Verify that DPDK role can be added after deploying.

        Scenario:
            1. Create an environment with "Neutron with tunneling
               segmentation" as a network configuration
            2. Enable and configure Contrail plugin
            3. Deploy cluster with following node configuration:
                node-01: 'controller', 'ceph-osd';
                node-02: 'contrail-config', 'contrail-control', 'contrail-db';
                node-03: 'contrail-db';
                node-04: 'compute', 'ceph-osd';
                node-05: 'compute', 'ceph-osd';
            4. Run OSTF tests
            6. Add one node with following configuration:
                node-6: "compute", "dpdk";
            7. Deploy changes
            8. Run OSTF tests

        """
        self.show_step(1)
        plugin.prepare_contrail_plugin(self, slaves=9,
                                       options={'images_ceph': True})
        self.bm_drv.host_prepare()

        self.show_step(2)
        # enable plugin in contrail settings
        plugin.activate_plugin(self)
        # activate DPDK feature
        plugin.activate_dpdk(self)
        # activate vSRX image
        vsrx_setup_result = plugin.activate_vsrx()

        plugin.show_range(self, 3, 5)
        conf_nodes = {
            'slave-01': ['controller', 'ceph-osd'],
            'slave-02': ['contrail-config',
                         'contrail-control',
                         'contrail-db'],
            'slave-03': ['contrail-db'],
            'slave-04': ['compute', 'ceph-osd'],
            'slave-05': ['compute', 'ceph-osd'],
        }
        self.fuel_web.update_nodes(
            self.cluster_id,
            nodes_dict=conf_nodes,
            update_interfaces=False)
        self.bm_drv.update_vm_node_interfaces(self, self.cluster_id)
        # Deploy cluster
        openstack.deploy_cluster(self)
        # Run OSTF tests
        if vsrx_setup_result:
            self.fuel_web.run_ostf(cluster_id=self.cluster_id)

        self.show_step(6)
        self.bm_drv.setup_fuel_node(self,
                                    cluster_id=self.cluster_id,
                                    roles=['compute', 'dpdk'])
        self.show_step(7)
        openstack.deploy_cluster(self)

        self.show_step(8)
        if vsrx_setup_result:
            self.fuel_web.run_ostf(cluster_id=self.cluster_id)

    @test(depends_on=[SetupEnvironment.prepare_slaves_9],
          groups=["contrail_dpdk_delete_dpdk"])
    @log_snapshot_after_test
    def contrail_dpdk_delete_dpdk(self):
        """Verify that DPDK role can be deleted after deploying.

        Scenario:
            1. Create an environment with "Neutron with tunneling
               segmentation" as a network configuration
            2. Enable and configure Contrail plugin
            3. Deploy cluster with following node configuration:
                node-01: 'controller', 'ceph-osd';
                node-02: 'contrail-control', 'contrail-config', 'contrail-db';
                node-03: 'contrail-db';
                node-04: 'compute', 'ceph-osd';
                node-05: 'ceph-osd', 'cinder';
                node-06: 'compute', 'dpdk';
            4. Run OSTF tests
            5. Delete node-06 with "dpdk" and "compute" roles
            6. Deploy changes
            7. Run OSTF tests

        """
        self.show_step(1)
        plugin.prepare_contrail_plugin(self, slaves=9,
                                       options={'images_ceph': True})
        self.bm_drv.host_prepare()

        self.show_step(2)
        # enable plugin in contrail settings
        plugin.activate_plugin(self)
        # activate DPDK feature
        plugin.activate_dpdk(self)
        # activate vSRX image
        vsrx_setup_result = plugin.activate_vsrx()

        plugin.show_range(self, 3, 4)
        self.bm_drv.setup_fuel_node(self,
                                    cluster_id=self.cluster_id,
                                    roles=['compute', 'dpdk'])
        conf_no_dpdk = {
            'slave-01': ['controller', 'ceph-osd'],
            'slave-02': ['contrail-control',
                         'contrail-config',
                         'contrail-db'],
            'slave-03': ['contrail-db'],
            'slave-04': ['compute', 'ceph-osd'],
            'slave-05': ['ceph-osd', 'cinder'],
        }

        self.fuel_web.update_nodes(
            self.cluster_id,
            nodes_dict=conf_no_dpdk,
            update_interfaces=False)
        self.bm_drv.update_vm_node_interfaces(self, self.cluster_id)
        # Deploy cluster
        openstack.deploy_cluster(self)
        # Run OSTF tests
        if vsrx_setup_result:
            self.fuel_web.run_ostf(cluster_id=self.cluster_id)

        self.show_step(5)
        self.bm_drv.setup_fuel_node(self,
                                    cluster_id=self.cluster_id,
                                    roles=['compute', 'dpdk'],
                                    pending_deletion=True,
                                    pending_addition=False)
        self.show_step(6)
        openstack.deploy_cluster(self)

        self.show_step(7)
        if vsrx_setup_result:
            self.fuel_web.run_ostf(cluster_id=self.cluster_id)
