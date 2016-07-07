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

from devops.helpers.helpers import wait

from fuelweb_test.helpers import os_actions
from fuelweb_test.helpers.decorators import log_snapshot_after_test
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
class SRIOVTests(TestBasic):
    """SRIOV Tests."""

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
            self.fuel_web.run_ostf(
                cluster_id=self.cluster_id,
                test_sets=['smoke', 'sanity', 'ha'],
                should_fail=1,
                failed_test_name=['Instance live migration'])

    @test(depends_on=[SetupEnvironment.prepare_slaves_9],
          groups=["contrail_sriov_add_compute"])
    @log_snapshot_after_test
    def contrail_sriov_add_compute(self):
        """Verify that Contrail compute role can be added after deploying.

        Scenario:
            1. Create an environment with "Neutron with tunneling
               segmentation" as a network configuration
            2. Enable and configure Contrail plugin
            3. Deploy cluster with following node configuration:
                node-1: 'controller', 'ceph-osd';
                node-2: 'contrail-config', 'contrail-control', 'contrail-db';
                node-3: 'contrail-db';
                node-4: 'compute', 'ceph-osd';
                node-5: 'compute', 'ceph-osd';
                node-7: 'compute', 'sriov';
            4. Run OSTF tests
            5. Add one node with following configuration:
                node-6: "compute", "ceph-osd";
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
        # enable plugin and enable SR-IOV in contrail settings
        plugin.activate_sriov(self)
        # activate vSRX image
        vsrx_setup_result = plugin.activate_vsrx()

        self.show_step(3)
        self.bm_drv.setup_fuel_node(self,
                                    cluster_id=self.cluster_id,
                                    roles=['compute', 'sriov'])
        conf_nodes = {
            'slave-01': ['controller', 'ceph-osd'],
            'slave-02': ['contrail-config',
                         'contrail-control',
                         'contrail-db'],
            'slave-03': ['contrail-db'],
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
        if vsrx_setup_result:
            self.fuel_web.run_ostf(cluster_id=self.cluster_id,
                                   should_fail=1,
                                   failed_test_name=['Instance live migration']
                                   )

    @test(depends_on=[SetupEnvironment.prepare_slaves_5],
          groups=["contrail_sriov_delete_compute"])
    @log_snapshot_after_test
    def contrail_sriov_delete_compute(self):
        """Verify that Contrail compute role can be deleted after deploying.

        Scenario:
            1. Create an environment with "Neutron with tunneling
               segmentation" as a network configuration
            2. Enable and configure Contrail plugin
            3. Deploy cluster with following node configuration:
                node-01: 'controller';
                node-02: 'contrail-control', 'contrail-db';
                node-03: 'contrail-config', 'contrail-db';
                node-04: 'compute', 'cinder';
                node-05: 'compute';
                node-bm: 'compute', 'sriov';
            4. Run OSTF tests
            5. Delete node-06 with "compute" role
            6. Deploy changes
            7. Run OSTF tests

        """
        self.show_step(1)
        plugin.prepare_contrail_plugin(self, slaves=9)
        self.bm_drv.host_prepare()

        self.show_step(2)
        # activate plugin with SRIOV feature
        plugin.activate_sriov(self)
        # activate vSRX image
        vsrx_setup_result = plugin.activate_vsrx()

        self.show_step(3)
        self.bm_drv.setup_fuel_node(self,
                                    cluster_id=self.cluster_id,
                                    roles=['compute', 'sriov'])
        conf_no_compute = {
            'slave-01': ['controller'],
            'slave-02': ['contrail-control',
                         'contrail-db'],
            'slave-03': ['contrail-config',
                         'contrail-db'],
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
          groups=["contrail_sriov_add_controller"])
    @log_snapshot_after_test
    def contrail_sriov_add_controller(self):
        """Verify that Contrail controller role can be added after deploying.

        Scenario:
            1. Create an environment with "Neutron with tunneling
               segmentation" as a network configuration
            2. Enable and configure Contrail plugin
            3. Deploy cluster with following node configuration:
                node-1: 'controller', 'ceph-osd';
                node-2: 'contrail-config', 'contrail-control', 'contrail-db';
                node-3: 'contrail-db';
                node-4: 'compute', 'ceph-osd';
                node-5: 'compute', 'ceph-osd';
                node-6: 'compute', 'sriov';
            4. Run OSTF tests
            5. Add one node with following configuration:
                node-7: "controller", "ceph-osd";
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
        # activate plugin with SRIOV feature
        plugin.activate_sriov(self)
        # activate vSRX image
        vsrx_setup_result = plugin.activate_vsrx()

        self.show_step(3)
        self.bm_drv.setup_fuel_node(self,
                                    cluster_id=self.cluster_id,
                                    roles=['compute', 'sriov'])
        conf_nodes = {
            'slave-01': ['controller', 'ceph-osd'],
            'slave-02': ['contrail-config',
                         'contrail-control',
                         'contrail-db'],
            'slave-03': ['contrail-db'],
            'slave-04': ['compute', 'ceph-osd'],
            'slave-05': ['compute', 'ceph-osd'],
        }
        conf_controller = {'slave-06': ['controller', 'ceph-osd']}

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
          groups=["contrail_sriov_delete_controller"])
    @log_snapshot_after_test
    def contrail_sriov_delete_controller(self):
        """Verify that Contrail controller role can be deleted after deploying.

        Scenario:
            1. Create an environment with "Neutron with tunneling
               segmentation" as a network configuration
            2. Enable and configure Contrail plugin
            3. Deploy cluster with following node configuration:
               node-01: 'controller';
               node-02: 'controller';
               node-03: 'contrail-control', 'contrail-config', 'contrail-db';
               node-04: 'contrail-db';
               node-05: 'compute', 'cinder';
               node-06: 'compute', 'sriov';
            4. Run OSTF tests
            5. Delete node-01 with "controller" role
            6. Deploy changes
            7. Run OSTF tests

        """
        self.show_step(1)
        plugin.prepare_contrail_plugin(self, slaves=9)
        self.bm_drv.host_prepare()

        self.show_step(2)
        # activate plugin with SRIOV feature
        plugin.activate_sriov(self)
        # activate vSRX image
        vsrx_setup_result = plugin.activate_vsrx()

        plugin.show_range(self, 3, 4)
        self.bm_drv.setup_fuel_node(self,
                                    cluster_id=self.cluster_id,
                                    roles=['compute', 'sriov'])
        conf_no_compute = {
            'slave-01': ['controller'],
            'slave-02': ['contrail-control',
                         'contrail-config',
                         'contrail-db'],
            'slave-03': ['contrail-db'],
            'slave-04': ['compute', 'cinder'],
        }
        conf_controller = {'slave-05': ['controller']}

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
          groups=["contrail_sriov_add_sriov"])
    @log_snapshot_after_test
    def contrail_sriov_add_sriov(self):
        """Verify that SRiOV role can be added after deploying.

        Scenario:
            1. Create an environment with "Neutron with tunneling
               segmentation" as a network configuration
            2. Enable and configure Contrail plugin
            3. Deploy cluster with following node configuration:
                node-01: 'controller', 'ceph-osd';
                node-02: 'contrail-config', 'contrail-control';
                node-03: 'contrail-db';
                node-04: 'compute', 'ceph-osd';
                node-05: 'compute', 'ceph-osd';
            4. Run OSTF tests
            6. Add one node with following configuration:
                node-bm: "compute", "sriov";
            7. Deploy changes
            8. Run OSTF tests

        """
        self.show_step(1)
        plugin.prepare_contrail_plugin(self, slaves=5,
                                       options={'images_ceph': True})
        self.bm_drv.host_prepare()

        self.show_step(2)
        # activate plugin with SRiOV feature
        plugin.activate_sriov(self)
        # activate vSRX image
        vsrx_setup_result = plugin.activate_vsrx()

        plugin.show_range(self, 3, 5)
        conf_nodes = {
            'slave-01': ['controller', 'ceph-osd'],
            'slave-02': ['contrail-config',
                         'contrail-control'],
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
                                    roles=['compute', 'sriov'])
        self.show_step(7)
        openstack.deploy_cluster(self)

        self.show_step(8)
        if vsrx_setup_result:
            self.fuel_web.run_ostf(cluster_id=self.cluster_id)

    @test(depends_on=[SetupEnvironment.prepare_slaves_9],
          groups=["contrail_sriov_delete_sriov"])
    @log_snapshot_after_test
    def contrail_sriov_delete_sriov(self):
        """Verify that SRiOV role can be deleted after deploying.

        Scenario:
            1. Create an environment with "Neutron with tunneling
               segmentation" as a network configuration
            2. Enable and configure Contrail plugin
            3. Deploy cluster with following node configuration:
                node-01: 'controller';
                node-02: 'controller';
                node-03: 'controller', 'cinder';
                node-04: 'contrail-control', 'contrail-config', 'contrail-db';
                node-05: 'contrail-control', 'contrail-config', 'contrail-db';
                node-06: 'contrail-control', 'contrail-config', 'contrail-db';
                node-07: 'compute';
                node-08: 'compute';
                node-bm: 'compute', 'sriov';
            4. Run OSTF tests
            5. Delete node-bm with "sriov" and "compute" roles
            6. Deploy changes
            7. Run OSTF tests

        """
        self.show_step(1)
        plugin.prepare_contrail_plugin(self, slaves=9)
        self.bm_drv.host_prepare()

        self.show_step(2)
        # activate plugin with SRiOV feature
        plugin.activate_sriov(self)
        # activate vSRX image
        vsrx_setup_result = plugin.activate_vsrx()

        self.show_step(3)
        self.bm_drv.setup_fuel_node(self,
                                    cluster_id=self.cluster_id,
                                    roles=['compute', 'sriov'])
        conf_no_dpdk = {
            'slave-01': ['controller'],
            'slave-02': ['controller'],
            'slave-03': ['controller', 'cinder'],
            'slave-04': ['contrail-control',
                         'contrail-config',
                         'contrail-db'],
            'slave-05': ['contrail-control',
                         'contrail-config',
                         'contrail-db'],
            'slave-06': ['contrail-control',
                         'contrail-config',
                         'contrail-db'],
            'slave-07': ['compute'],
            'slave-08': ['compute']
        }

        self.fuel_web.update_nodes(
            self.cluster_id,
            nodes_dict=conf_no_dpdk,
            update_interfaces=False)
        self.bm_drv.update_vm_node_interfaces(self, self.cluster_id)
        # Deploy cluster
        openstack.deploy_cluster(self)
        # Run OSTF tests
        self.show_step(4)
        if vsrx_setup_result:
            self.fuel_web.run_ostf(cluster_id=self.cluster_id)

        self.show_step(5)
        self.bm_drv.setup_fuel_node(self,
                                    cluster_id=self.cluster_id,
                                    roles=['compute', 'sriov'],
                                    pending_deletion=True,
                                    pending_addition=False)
        self.show_step(6)
        openstack.deploy_cluster(self)

        self.show_step(7)
        if vsrx_setup_result:
            self.fuel_web.run_ostf(cluster_id=self.cluster_id,
                                   should_fail=1,
                                   failed_test_name=['Check that required '
                                                     'services are running']
                                   )

    @test(depends_on=[SetupEnvironment.prepare_slaves_5],
          groups=["contrail_sriov_setup"])
    @log_snapshot_after_test
    def contrail_sriov_setup(self):
        """Contrail SRIOV setup.

        Scenario:
            1. Create an environment with "Neutron with tunneling
               segmentation" as a network configuration and CEPH storage.
            2. Enable and configure Contrail plugin.
            3. Enable sriov.
            4. Deploy cluster with following node configuration:
                node-01: 'controller', 'ceph-osd';
                node-02: 'compute';
                node-03: 'contrail-db', 'contrail-config', 'contrail-control';
                node-sriov: 'compute', sriov'.
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
        # enable plugin and ativate SR-IOV in contrail settings
        plugin.activate_sriov(self)
        # activate vSRX image
        vsrx_setup_result = plugin.activate_vsrx()

        self.show_step(4)
        self.bm_drv.setup_fuel_node(self,
                                    cluster_id=self.cluster_id,
                                    roles=['compute', 'sriov'])

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

    @test(depends_on=[contrail_sriov_setup],
          groups=["contrail_sriov_boot_snapshot_vm"])
    @log_snapshot_after_test
    def contrail_sriov_boot_snapshot_vm(self):
        """Launch instance, create snapshot, launch instance from snapshot.

        Scenario:
            1. Setup contrail_sriov_setup.
            2. Create physical network.
            3. Create a subnet.
            4. Create a port.
            5. Boot the instance with the port on the SRIOV host.
            6. Create snapshot of instance.
            7. Delete the instance created in step 5.
            8. Launch instance from snapshot.
            9. Delete the instance created in step 8.

        Duration 5 min

        """
        net_name = 'sriov'
        subnet_cidr = '192.168.112.0/24'
        cluster_id = self.fuel_web.get_last_created_cluster()
        binding_port = 'direct'

        self.show_step(2)
        os_ip = self.fuel_web.get_public_vip(cluster_id)
        os_conn = os_actions.OpenStackActions(
            os_ip, SERVTEST_USERNAME,
            SERVTEST_PASSWORD,
            SERVTEST_TENANT)

        body = {
            'network': {
                'name': net_name,
                'provider:physical_network': 'physnet1',
                'provider:segmentation_id': '5'}}
        network = os_conn.neutron.create_network(body)['network']

        self.show_step(3)
        os_conn.create_subnet(
            subnet_name=net_name,
            network_id=network['id'],
            cidr=subnet_cidr,
            ip_version=4)

        self.show_step(4)

        port = os_conn.neutron.create_port(
            {"port": {
                "network_id": network['id'],
                "binding:vnic_type": binding_port}})['port']

        self.show_step(5)
        images_list = os_conn.nova.images.list()
        flavors = os_conn.nova.flavors.list()
        flavor = [f for f in flavors if f.name == 'm1.micro'][0]

        srv_1 = os_conn.nova.servers.create(
            flavor=flavor, name='test1',
            image=images_list[0], nics=[{'port-id': port['id']}])

        openstack.verify_instance_state(os_conn)

        self.show_step(6)
        image = os_conn.nova.servers.create_image(srv_1, 'image1')
        wait(lambda: os_conn.nova.images.get(image).status == 'ACTIVE',
             timeout=300, timeout_msg='Image is not active.')

        self.show_step(7)
        os_conn.delete_instance(srv_1)
        assert_true(
            os_conn.verify_srv_deleted(srv_1),
            "Instance was not deleted.")

        self.show_step(8)
        port = os_conn.neutron.create_port(
            {"port": {
                "network_id": network['id'],
                "binding:vnic_type": binding_port}})['port']

        srv_2 = os_conn.nova.servers.create(
            flavor=flavor, name='test1',
            image=image, nics=[{'port-id': port['id']}])
        openstack.verify_instance_state(os_conn, instances=[srv_2])

        self.show_step(9)
        os_conn.delete_instance(srv_2)
        assert_true(
            os_conn.verify_srv_deleted(srv_2),
            "Instance was not deleted.")

    @test(depends_on=[contrail_sriov_setup],
          groups=["contrail_sriov_volume"])
    @log_snapshot_after_test
    def contrail_sriov_volume(self):
        """Create volume and boot instance from it.

        Scenario:
            1. Setup contrail_sriov_setup.
            2. Create physical network.
            3. Create a subnet.
            4. Create a port.
            5. Create a new small-size volume from image.
            6. Wait for volume status to become "available".
            7. Launch instance from created volume and port on the SRIOV host.
            8. Wait for "Active" status.
            9. Delete instance.
            10. Delete volume and verify that volume deleted.

        Duration 5 min

        """
        net_name = 'sriov'
        subnet_cidr = '192.168.112.0/24'
        cluster_id = self.fuel_web.get_last_created_cluster()
        binding_port = 'direct'

        self.show_step(2)
        os_ip = self.fuel_web.get_public_vip(cluster_id)
        os_conn = os_actions.OpenStackActions(
            os_ip, SERVTEST_USERNAME,
            SERVTEST_PASSWORD,
            SERVTEST_TENANT)

        body = {
            'network': {
                'name': net_name,
                'provider:physical_network': 'physnet1',
                'provider:segmentation_id': '5'}}
        network = os_conn.neutron.create_network(body)['network']

        self.show_step(3)
        os_conn.create_subnet(
            subnet_name=net_name,
            network_id=network['id'],
            cidr=subnet_cidr,
            ip_version=4)

        self.show_step(4)

        port = os_conn.neutron.create_port(
            {"port": {
                "network_id": network['id'],
                "binding:vnic_type": binding_port}})['port']

        plugin.show_range(self, 5, 7)
        images_list = os_conn.nova.images.list()
        flavors = os_conn.nova.flavors.list()
        flavor = [f for f in flavors if f.name == 'm1.micro'][0]
        volume = os_conn.create_volume(image_id=images_list[0].id)

        self.show_step(7)
        srv_1 = os_conn.nova.servers.create(
            flavor=flavor, name='test1',
            image=images_list[0],
            block_device_mapping={'vda': volume.id + ':::0'},
            nics=[{'port-id': port['id']}])

        self.show_step(8)
        openstack.verify_instance_state(os_conn, instances=[srv_1])

        self.show_step(9)
        os_conn.delete_instance(srv_1)
        assert_true(os_conn.verify_srv_deleted(srv_1),
                    "Instance was not deleted.")

        self.show_step(10)
        os_conn.delete_volume_and_wait(volume)
