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
from proboscis.asserts import assert_true

from devops.helpers.helpers import tcp_ping
from devops.helpers.helpers import wait

from fuelweb_test.helpers.decorators import log_snapshot_after_test
from fuelweb_test.helpers import os_actions
from fuelweb_test.settings import CONTRAIL_PLUGIN_PACK_UB_PATH
from fuelweb_test.settings import SERVTEST_PASSWORD
from fuelweb_test.settings import SERVTEST_TENANT
from fuelweb_test.settings import SERVTEST_USERNAME
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
          groups=["contrail_ha_dpdk", "contrail_dpdk_tests"])
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
        # activate plugin with DPDK feature
        plugin.activate_dpdk(self)
        # activate vSRX image
        vsrx_setup_result = plugin.activate_vsrx()

        self.show_step(3)
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
        # FIXME: remove shouldfail, when livemigration+DPDK works
        if vsrx_setup_result:
            self.show_step(4)
            self.fuel_web.run_ostf(cluster_id=self.cluster_id,
                                   test_sets=['smoke', 'sanity', 'ha'],
                                   should_fail=1,
                                   failed_test_name=['Instance live migration']
                                   )

    @test(depends_on=[SetupEnvironment.prepare_slaves_9],
          groups=["contrail_dpdk_add_compute", "contrail_dpdk_tests"])
    @log_snapshot_after_test
    def contrail_dpdk_add_compute(self):
        """Verify that Contrail compute role can be added after deploying.

        Scenario:
            1. Create an environment with "Neutron with tunneling
               segmentation" as a network configuration
            2. Enable and configure Contrail plugin
            3. Deploy cluster with following node configuration:
                node-1: 'controller', 'ceph-osd';
                node-2: 'contrail-config', 'contrail-control',
                    'contrail-db', 'contrail-analytics';
                node-3: 'compute', 'ceph-osd';
                node-4: 'compute', 'ceph-osd';
                node-dpdk: 'compute', 'dpdk';
            4. Run OSTF tests
            5. Add one node with following configuration:
                node-5: "compute", "ceph-osd";
            6. Deploy changes
            7. Run OSTF tests

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
        # activate plugin with DPDK feature
        plugin.activate_dpdk(self)
        # activate vSRX image
        vsrx_setup_result = plugin.activate_vsrx()

        self.show_step(3)
        self.bm_drv.setup_fuel_node(self,
                                    cluster_id=self.cluster_id,
                                    roles=['compute', 'dpdk'])
        conf_nodes = {
            'slave-01': ['controller', 'ceph-osd'],
            'slave-02': ['contrail-config',
                         'contrail-control',
                         'contrail-db',
                         'contrail-analytics'],
            'slave-03': ['compute', 'ceph-osd'],
            'slave-04': ['compute', 'ceph-osd'],
            'slave-05': ['compute', 'ceph-osd'],
        }
        conf_compute = {'slave-06': ['compute', 'ceph-osd']}

        # Cluster configuration
        self.fuel_web.update_nodes(self.cluster_id,
                                   nodes_dict=conf_nodes,
                                   update_interfaces=False)
        self.bm_drv.update_vm_node_interfaces(self, self.cluster_id)
        # Deploy cluster
        openstack.deploy_cluster(self)
        # Run OSTF tests
        self.show_step(4)
        # FIXME: remove shouldfail, when livemigration+DPDK works
        if vsrx_setup_result:
            self.fuel_web.run_ostf(cluster_id=self.cluster_id,
                                   should_fail=1,
                                   failed_test_name=['Instance live migration']
                                   )

        # Add Compute node and check again
        self.show_step(5)
        # Cluster configuration
        self.fuel_web.update_nodes(self.cluster_id,
                                   nodes_dict=conf_compute,
                                   update_interfaces=False)
        self.bm_drv.update_vm_node_interfaces(self, self.cluster_id)
        # Deploy cluster
        self.show_step(6)
        openstack.deploy_cluster(self)
        # Run OSTF tests
        self.show_step(7)
        # FIXME: remove shouldfail, when livemigration+DPDK works
        if vsrx_setup_result:
            self.fuel_web.run_ostf(cluster_id=self.cluster_id,
                                   should_fail=1,
                                   failed_test_name=['Instance live migration']
                                   )

    @test(depends_on=[SetupEnvironment.prepare_slaves_9],
          groups=["contrail_dpdk_delete_compute", "contrail_dpdk_tests"])
    @log_snapshot_after_test
    def contrail_dpdk_delete_compute(self):
        """Verify that Contrail compute role can be deleted after deploying.

        Scenario:
            1. Create an environment with "Neutron with tunneling
               segmentation" as a network configuration
            2. Enable and configure Contrail plugin
            3. Deploy cluster with following node configuration:
                node-01: 'controller';
                node-02: 'contrail-control', 'contrail-config',
                    'contrail-db', 'contrail-analytics';
                node-03: 'contrail-db';
                node-04: 'compute', 'cinder';
                node-05: 'compute';
                node-06: 'contrail-db';
            4. Run OSTF tests
            5. Delete node-05 with "compute" role
            6. Deploy changes
            7. Run OSTF tests

        """
        self.show_step(1)
        plugin.prepare_contrail_plugin(self, slaves=9)
        self.bm_drv.host_prepare()

        self.show_step(2)
        # activate plugin with DPDK feature
        plugin.activate_dpdk(self)
        # activate vSRX image
        vsrx_setup_result = plugin.activate_vsrx()

        self.show_step(3)
        self.bm_drv.setup_fuel_node(self,
                                    cluster_id=self.cluster_id,
                                    roles=['compute', 'dpdk'])
        conf_no_compute = {
            'slave-01': ['controller'],
            'slave-02': ['contrail-control',
                         'contrail-config',
                         'contrail-db',
                         'contrail-analytics'],
            'slave-03': ['contrail-db'],
            'slave-04': ['compute', 'cinder'],
            # node-05
            'slave-06': ['contrail-db'],
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
            self.show_step(4)
            self.fuel_web.run_ostf(cluster_id=self.cluster_id)

        # Delete Compute node and check again
        self.show_step(5)
        self.fuel_web.update_nodes(
            self.cluster_id,
            nodes_dict=conf_compute,
            pending_addition=False, pending_deletion=True,
            update_interfaces=False)

        # Deploy cluster
        self.show_step(6)
        openstack.deploy_cluster(self)
        # Run OSTF tests
        if vsrx_setup_result:
            self.show_step(7)
            self.fuel_web.run_ostf(cluster_id=self.cluster_id,
                                   test_sets=['smoke', 'sanity'],
                                   should_fail=1,
                                   failed_test_name=['Check that required '
                                                     'services are running']
                                   )

    @test(depends_on=[SetupEnvironment.prepare_slaves_9],
          groups=["contrail_dpdk_add_dpdk", "contrail_dpdk_tests"])
    @log_snapshot_after_test
    def contrail_dpdk_add_dpdk(self):
        """Verify that DPDK role can be added after deploying.

        Scenario:
            1. Create an environment with "Neutron with tunneling
               segmentation" as a network configuration
            2. Enable and configure Contrail plugin
            3. Deploy cluster with following node configuration:
                node-01: 'controller', 'ceph-osd';
                node-02: 'contrail-config', 'contrail-control',
                    'contrail-db', 'contrail-analytics';
                node-03: 'compute', 'ceph-osd';
                node-04: 'compute', 'ceph-osd';
                node-05: 'controller', 'cinder';
                node-06: 'controller', 'cinder';
            4. Run OSTF tests
            6. Add one node with following configuration:
                node-dpdk: "compute", "dpdk";
            7. Deploy changes
            8. Run OSTF tests

        """
        self.show_step(1)
        plugin.prepare_contrail_plugin(self, slaves=9,
                                       options={'images_ceph': True})
        self.bm_drv.host_prepare()

        self.show_step(2)
        # activate plugin with DPDK feature
        plugin.activate_dpdk(self)
        # activate vSRX image
        vsrx_setup_result = plugin.activate_vsrx()

        plugin.show_range(self, 3, 5)
        conf_nodes = {
            'slave-01': ['controller', 'ceph-osd'],
            'slave-02': ['contrail-config',
                         'contrail-control',
                         'contrail-db',
                         'contrail-analytics'],
            'slave-03': ['compute', 'ceph-osd'],
            'slave-04': ['compute', 'ceph-osd'],
            'slave-05': ['controller', 'cinder'],
            'slave-06': ['controller', 'cinder'],
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
            self.fuel_web.run_ostf(cluster_id=self.cluster_id,
                                   test_sets=['smoke', 'sanity', 'ha'])

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
          groups=["contrail_dpdk_delete_dpdk", "contrail_dpdk_tests"])
    @log_snapshot_after_test
    def contrail_dpdk_delete_dpdk(self):
        """Verify that DPDK role can be deleted after deploying.

        Scenario:
            1. Create an environment with "Neutron with tunneling
               segmentation" as a network configuration
            2. Enable and configure Contrail plugin
            3. Deploy cluster with following node configuration:
                node-01: 'controller', 'ceph-osd', 'cinder';
                node-02: 'contrail-control', 'contrail-config',
                    'contrail-db', 'contrail-analytics';
                node-03: 'compute', 'ceph-osd';
                node-04: 'compute', 'ceph-osd';
                node-dpdk: 'compute', 'dpdk';
            4. Run OSTF tests
            5. Delete node "node-dpdk" with "dpdk" and "compute" roles
            6. Deploy changes
            7. Run OSTF tests

        """
        self.show_step(1)
        plugin.prepare_contrail_plugin(self, slaves=9,
                                       options={'images_ceph': True})
        self.bm_drv.host_prepare()

        self.show_step(2)
        # activate plugin with DPDK feature
        plugin.activate_dpdk(self)
        # activate vSRX image
        vsrx_setup_result = plugin.activate_vsrx()

        plugin.show_range(self, 3, 4)
        self.bm_drv.setup_fuel_node(self,
                                    cluster_id=self.cluster_id,
                                    roles=['compute', 'dpdk'])
        conf_no_dpdk = {
            'slave-01': ['controller', 'ceph-osd', 'cinder'],
            'slave-02': ['contrail-control',
                         'contrail-config',
                         'contrail-db',
                         'contrail-analytics'],
            'slave-03': ['compute', 'ceph-osd'],
            'slave-04': ['compute', 'ceph-osd'],
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
            self.fuel_web.run_ostf(cluster_id=self.cluster_id,
                                   test_sets=['smoke', 'sanity'],
                                   should_fail=1,
                                   failed_test_name=['Check that required '
                                                     'services are running']
                                   )

    @test(depends_on=[SetupEnvironment.prepare_slaves_9],
          groups=["contrail_dpdk_add_controller", "contrail_dpdk_tests"])
    @log_snapshot_after_test
    def contrail_dpdk_add_controller(self):
        """Verify that Contrail controller role can be added after deploying.

        Scenario:
            1. Create an environment with "Neutron with tunneling
               segmentation" as a network configuration
            2. Enable and configure Contrail plugin
            3. Deploy cluster with following node configuration:
                node-1: 'controller', 'ceph-osd';
                node-2: 'contrail-config', 'contrail-control',
                    'contrail-db', 'contrail-analytics';
                node-3: 'compute', 'ceph-osd';
                node-4: 'compute', 'ceph-osd';
            4. Run OSTF tests
            5. Add one node with following configuration:
                node-5: 'controller', 'ceph-osd';
            6. Deploy changes
            7. Run OSTF tests

        """
        self.show_step(1)
        plugin.prepare_contrail_plugin(self, slaves=5,
                                       options={'images_ceph': True,
                                                'volumes_ceph': True,
                                                'ephemeral_ceph': True,
                                                'objects_ceph': True,
                                                'volumes_lvm': False})
        self.bm_drv.host_prepare()

        self.show_step(2)
        # activate plugin with DPDK feature
        plugin.activate_dpdk(self)
        # activate vSRX image
        vsrx_setup_result = plugin.activate_vsrx()

        self.show_step(3)
        self.bm_drv.setup_fuel_node(self,
                                    cluster_id=self.cluster_id,
                                    roles=['compute', 'dpdk'])
        conf_nodes = {
            'slave-01': ['controller', 'ceph-osd'],
            'slave-02': ['contrail-config',
                         'contrail-control',
                         'contrail-db',
                         'contrail-analytics'],
            'slave-03': ['compute', 'ceph-osd'],
            'slave-04': ['compute', 'ceph-osd'],
        }
        conf_controller = {'slave-05': ['controller', 'ceph-osd']}

        # Cluster configuration
        self.fuel_web.update_nodes(self.cluster_id,
                                   nodes_dict=conf_nodes,
                                   update_interfaces=False)
        self.bm_drv.update_vm_node_interfaces(self, self.cluster_id)
        # Deploy cluster
        openstack.deploy_cluster(self)
        # Run OSTF tests
        self.show_step(4)
        # FIXME: remove shouldfail, when livemigration+DPDK works
        if vsrx_setup_result:
            self.fuel_web.run_ostf(cluster_id=self.cluster_id,
                                   should_fail=1,
                                   failed_test_name=['Instance live migration']
                                   )

        # Add Compute node and check again
        self.show_step(5)
        # Cluster configuration
        self.fuel_web.update_nodes(self.cluster_id,
                                   nodes_dict=conf_controller,
                                   update_interfaces=False)
        self.bm_drv.update_vm_node_interfaces(self, self.cluster_id)
        # Deploy cluster
        self.show_step(6)
        openstack.deploy_cluster(self)
        # Run OSTF tests
        self.show_step(7)
        # FIXME: remove shouldfail, when livemigration+DPDK works
        if vsrx_setup_result:
            self.fuel_web.run_ostf(cluster_id=self.cluster_id,
                                   should_fail=1,
                                   failed_test_name=['Instance live migration']
                                   )

    @test(depends_on=[SetupEnvironment.prepare_slaves_9],
          groups=["contrail_dpdk_delete_controller", "contrail_dpdk_tests"])
    @log_snapshot_after_test
    def contrail_dpdk_delete_controller(self):
        """Verify that Contrail controller role can be deleted after deploying.

        Scenario:
            1. Create an environment with "Neutron with tunneling
               segmentation" as a network configuration
            2. Enable and configure Contrail plugin
            3. Deploy cluster with following node configuration:
                node-01: 'controller';
                node-02: 'contrail-control', 'contrail-config',
                    'contrail-db', 'contrail-analytics';
                node-03: 'controller';
                node-04: 'compute', 'cinder';
                node-05: 'controller';
            4. Run OSTF tests
            5. Delete node-01 with "controller" role
            6. Deploy changes
            7. Run OSTF tests

        """
        self.show_step(1)
        plugin.prepare_contrail_plugin(self, slaves=5)
        self.bm_drv.host_prepare()

        self.show_step(2)
        # activate plugin with DPDK feature
        plugin.activate_dpdk(self)
        # activate vSRX image
        vsrx_setup_result = plugin.activate_vsrx()

        plugin.show_range(self, 3, 4)
        self.bm_drv.setup_fuel_node(self,
                                    cluster_id=self.cluster_id,
                                    roles=['compute', 'dpdk'])
        conf_no_compute = {
            'slave-01': ['controller'],
            'slave-02': ['contrail-control',
                         'contrail-config',
                         'contrail-db',
                         'contrail-analytics'],
            'slave-03': ['controller'],
            'slave-04': ['compute', 'cinder'],
            'slave-05': ['controller'],
        }
        conf_controller = {'slave-01': ['controller']}

        self.fuel_web.update_nodes(
            self.cluster_id,
            nodes_dict=dict(conf_no_compute, **conf_controller),
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
            nodes_dict=conf_controller,
            pending_addition=False, pending_deletion=True,
            update_interfaces=False)

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

    @test(depends_on=[SetupEnvironment.prepare_slaves_5],
          groups=["contrail_add_to_dpdk_sriov", "contrail_dpdk_tests"])
    @log_snapshot_after_test
    def contrail_add_to_dpdk_sriov(self):
        """Verify that Contrail controller role can be added after deploying.

        Scenario:
            1. Create an environment with "Neutron with tunneling segmentation"
                as a network configuration
            2. Enable and configure Contrail plugin
            3. Enable dpdk and sriov
            4. Add dpdk and sriov nodes
            5. Deploy cluster with following node configuration:
                node-2: 'contrail-config', 'contrail-control',
                    'contrail-db', 'contrail-analytics';
                node-3: 'compute', 'cinder';
                node-4: 'contrail-config', 'contrail-control',
                    'contrail-db', 'contrail-analytics';
                node-5: 'contrail-config', 'contrail-control',
                    'contrail-db', 'contrail-analytics';
            6. Run OSTF
            7. Add one node with following configuration:
                node-1: 'controller';
            8. Deploy changes
            9. Run OSTF
        """
        plugin.show_range(self, 1, 3)
        plugin.prepare_contrail_plugin(self, slaves=5)
        self.bm_drv.host_prepare()

        self.show_step(3)
        # activate plugin with DPDK feature
        plugin.activate_dpdk(self)
        # enable plugin and ativate SR-IOV in contrail settings
        plugin.activate_sriov(self)
        # activate vSRX image
        vsrx_setup_result = plugin.activate_vsrx()

        self.show_step(4)
        self.bm_drv.setup_fuel_node(self,
                                    cluster_id=self.cluster_id,
                                    roles=['compute', 'dpdk', 'sriov'])
        conf_nodes = {
            # node-01
            'slave-02': ['contrail-config', 'contrail-control',
                         'contrail-db', 'contrail-analytics'],
            'slave-03': ['compute', 'cinder'],
            'slave-04': ['contrail-config', 'contrail-control',
                         'contrail-db', 'contrail-analytics'],
            'slave-05': ['contrail-config', 'contrail-control',
                         'contrail-db', 'contrail-analytics'],
        }
        conf_controller = {'slave-01': ['controller']}

        # Cluster configuration
        self.fuel_web.update_nodes(self.cluster_id,
                                   nodes_dict=conf_nodes,
                                   update_interfaces=False)
        self.bm_drv.update_vm_node_interfaces(self, self.cluster_id)
        # Deploy cluster
        self.show_step(5)
        openstack.deploy_cluster(self)
        # Run OSTF tests
        if vsrx_setup_result:
            self.show_step(6)
            self.fuel_web.run_ostf(cluster_id=self.cluster_id)

        # Add Contrail node and check again
        self.show_step(7)
        # Cluster configuration
        self.fuel_web.update_nodes(self.cluster_id,
                                   nodes_dict=conf_controller,
                                   update_interfaces=False)
        self.bm_drv.update_vm_node_interfaces(self, self.cluster_id)
        # Deploy cluster
        self.show_step(8)
        openstack.deploy_cluster(self)
        # Run OSTF tests
        if vsrx_setup_result:
            self.show_step(9)
            self.fuel_web.run_ostf(cluster_id=self.cluster_id)

    @test(depends_on=[SetupEnvironment.prepare_slaves_5],
          groups=["contrail_dpdk_setup", "contrail_dpdk_tests"])
    @log_snapshot_after_test
    def contrail_dpdk_setup(self):
        """Contrail DPDK setup.

        Scenario:
            1. Create an environment with "Neutron with tunneling
               segmentation" as a network configuration and CEPH storage.
            2. Enable and configure Contrail plugin.
            3. Enable dpdk.
            4. Deploy cluster with following node configuration:
                node-01: 'controller', 'ceph-osd';
                node-02: 'compute';
                node-03: 'contrail-db', 'contrail-config', 'contrail-control';
                node-dpdk: 'compute', dpdk'.
            5. Run OSTF tests.

        Duration 120 min

        """
        self.show_step(1)
        plugin.prepare_contrail_plugin(self, slaves=5,
                                       options={'images_ceph': True,
                                                'volumes_ceph': True,
                                                'ephemeral_ceph': True,
                                                'objects_ceph': True,
                                                'volumes_lvm': False,
                                                'osd_pool_size': '1'})
        self.bm_drv.host_prepare()

        plugin.show_range(self, 2, 4)
        # enable plugin and ativate DPDK in contrail settings
        plugin.activate_dpdk(self)
        # activate vSRX image
        vsrx_setup_result = plugin.activate_vsrx()

        self.show_step(4)
        self.bm_drv.setup_fuel_node(self,
                                    cluster_id=self.cluster_id,
                                    roles=['compute', 'dpdk'])

        conf_nodes = {
            'slave-01': ['controller', 'ceph-osd'],
            'slave-02': ['compute'],
            'slave-03': ['contrail-db', 'contrail-config', 'contrail-control'],
        }
        # Cluster configurationeplication factor
        self.fuel_web.update_nodes(self.cluster_id,
                                   nodes_dict=conf_nodes,
                                   update_interfaces=False)
        self.bm_drv.update_vm_node_interfaces(self, self.cluster_id)

        # Deploy cluster
        openstack.deploy_cluster(self)

        self.show_step(5)
        # Run OSTF tests
        if vsrx_setup_result:
            self.fuel_web.run_ostf(
                cluster_id=self.cluster_id,
                test_sets=['smoke', 'sanity', 'ha'],
                should_fail=1,
                failed_test_name=['Instance live migration'])

    @test(depends_on=[contrail_dpdk_setup],
          groups=["contrail_dpdk_boot_snapshot_vm", "contrail_dpdk_tests"])
    @log_snapshot_after_test
    def contrail_dpdk_boot_snapshot_vm(self):
        """Launch instance, create snapshot, launch instance from snapshot.

        Scenario:
            1. Setup contrail_dpdk_setup.
            2. Create no default network with subnet.
            3. Get existing flavor with hpgs.
            4. Launch an instance using the default image and flavor with hpgs
               in the hpgs availability zone.
            5. Make snapshot of the created instance.
            6. Delete the last created instance.
            7. Launch another instance from the snapshot created in step 5.
               and flavor with hpgs in the hpgs availability zone.
            8. Delete the last created instance.

        Duration 5 min

        """
        az_name = 'hpgs'
        subnet_cidr = '192.168.112.0/24'
        cluster_id = self.fuel_web.get_last_created_cluster()
        net_name = 'net_1'

        self.show_step(2)
        os_ip = self.fuel_web.get_public_vip(cluster_id)
        os_conn = os_actions.OpenStackActions(
            os_ip, SERVTEST_USERNAME,
            SERVTEST_PASSWORD,
            SERVTEST_TENANT)

        network = os_conn.create_network(
            network_name=net_name)['network']
        os_conn.create_subnet(
            subnet_name=net_name,
            network_id=network['id'],
            cidr=subnet_cidr,
            ip_version=4)

        self.show_step(3)
        flavor = [
            f for f in os_conn.nova.flavors.list()
            if az_name in f.name][0]

        self.show_step(4)
        srv_1 = os_conn.create_server_for_migration(
            neutron=True, availability_zone=az_name,
            label=net_name, flavor=flavor)

        self.show_step(5)
        image = os_conn.nova.servers.create_image(srv_1, 'image1')
        wait(lambda: os_conn.nova.images.get(image).status == 'ACTIVE',
             timeout=300, timeout_msg='Image is not active.')

        self.show_step(6)
        os_conn.delete_instance(srv_1)
        assert_true(
            os_conn.verify_srv_deleted(srv_1),
            "Instance was not deleted.")

        self.show_step(7)
        srv_2 = os_conn.nova.servers.create(
            flavor=flavor, name='srv_2', image=image,
            availability_zone=az_name, nics=[{'net-id': network['id']}])
        openstack.verify_instance_state(os_conn, instances=[srv_2])

        self.show_step(8)
        os_conn.delete_instance(srv_2)
        assert_true(
            os_conn.verify_srv_deleted(srv_2),
            "Instance was not deleted.")

    @test(depends_on=[contrail_dpdk_setup],
          groups=["contrail_dpdk_volume", "contrail_dpdk_tests"])
    @log_snapshot_after_test
    def contrail_dpdk_volume(self):
        """Create volume and boot instance from it.

        Scenario:
            1. Setup contrail_dpdk_setup.
            2. Create no default network with subnet.
            3. Get existing flavor with hpgs.
            4. Create a new small-size volume from image.
            5. Wait for volume status to become "available".
            6. Launch an instance using the default image and flavor with hpgs
               in the hpgs availability zone.
            7. Wait for "Active" status.
            8. Delete the last created instance.
            9. Delete volume and verify that volume deleted.

        Duration 5 min

        """
        az_name = 'hpgs'
        subnet_cidr = '192.168.112.0/24'
        cluster_id = self.fuel_web.get_last_created_cluster()
        net_name = 'net_1'

        self.show_step(2)
        os_ip = self.fuel_web.get_public_vip(cluster_id)
        os_conn = os_actions.OpenStackActions(
            os_ip, SERVTEST_USERNAME,
            SERVTEST_PASSWORD,
            SERVTEST_TENANT)

        network = os_conn.create_network(
            network_name=net_name)['network']
        os_conn.create_subnet(
            subnet_name=net_name,
            network_id=network['id'],
            cidr=subnet_cidr,
            ip_version=4)

        self.show_step(3)
        flavor = [
            f for f in os_conn.nova.flavors.list()
            if az_name in f.name][0]

        plugin.show_range(self, 4, 6)
        images_list = os_conn.nova.images.list()
        volume = os_conn.create_volume(image_id=images_list[0].id)

        self.show_step(6)
        srv_1 = os_conn.create_server_for_migration(
            neutron=True, availability_zone=az_name,
            label=net_name, flavor=flavor,
            block_device_mapping={'vda': volume.id + ':::0'})

        self.show_step(7)
        openstack.verify_instance_state(os_conn, instances=[srv_1])

        self.show_step(8)
        os_conn.delete_instance(srv_1)
        assert_true(
            os_conn.verify_srv_deleted(srv_1),
            "Instance was not deleted.")

        self.show_step(9)
        os_conn.delete_volume_and_wait(volume)

    @test(depends_on=[contrail_dpdk_setup],
          groups=["contrail_dpdk_check_public_connectivity_from_instance",
                  "contrail_dpdk_tests"])
    @log_snapshot_after_test
    def contrail_dpdk_check_public_connectivity_from_instance(self):
        """Check network connectivity from instance via floating IP.

        Scenario:
            1. Setup contrail_dpdk_setup.
            2. Create no default network with subnet.
            3. Create Router_01, set gateway and add interface
               to external network.
            4. Get existing flavor with hpgs.
            5. Create a new security group (if it doesn`t exist yet).
            6. Launch an instance using the default image and flavor with hpgs
               in the hpgs availability zone.
            7. Create a new floating IP.
            8. Assign the new floating IP to the instance.
            9. Check connectivity to the floating IP using ping command.
            10. Check that public IP 8.8.8.8 can be pinged from instance.
            11. Delete instance.

        Duration 5 min

        """
        az_name = 'hpgs'
        subnet_cidr = '192.168.112.0/24'
        cluster_id = self.fuel_web.get_last_created_cluster()
        net_name = 'net_1'
        ping_command = "ping -c 5 8.8.8.8"

        self.show_step(2)
        os_ip = self.fuel_web.get_public_vip(cluster_id)
        os_conn = os_actions.OpenStackActions(
            os_ip, SERVTEST_USERNAME,
            SERVTEST_PASSWORD,
            SERVTEST_TENANT)

        network = os_conn.create_network(
            network_name=net_name)['network']
        subnet = os_conn.create_subnet(
            subnet_name=net_name,
            network_id=network['id'],
            cidr=subnet_cidr,
            ip_version=4)

        self.show_step(3)
        gateway = {
            "network_id": os_conn.get_network('admin_floating_net')['id'],
            "enable_snat": True}
        router_param = {'router': {
            'name': 'df', 'external_gateway_info': gateway}}
        router = os_conn.neutron.create_router(body=router_param)['router']
        os_conn.add_router_interface(
            router_id=router["id"],
            subnet_id=subnet["id"])

        self.show_step(4)
        flavor = [
            f for f in os_conn.nova.flavors.list()
            if az_name in f.name][0]

        plugin.show_range(self, 5, 7)
        srv = os_conn.create_server_for_migration(
            neutron=True, availability_zone=az_name,
            label=net_name, flavor=flavor)

        plugin.show_range(self, 7, 9)
        fip = os_conn.assign_floating_ip(srv).ip

        self.show_step(9)
        wait(
            lambda: tcp_ping(fip, 22), timeout=120, interval=5,
            timeout_msg="Node {0} is not accessible by SSH.".format(fip))

        self.show_step(10)
        with self.fuel_web.get_ssh_for_node("slave-01") as remote:
            assert_true(
                os_conn.execute_through_host(
                    remote, fip, ping_command)['exit_code'] == 0,
                'Ping responce is not received.')

        self.show_step(11)
        os_conn.delete_instance(srv)
        assert_true(
            os_conn.verify_srv_deleted(srv),
            "Instance was not deleted.")
