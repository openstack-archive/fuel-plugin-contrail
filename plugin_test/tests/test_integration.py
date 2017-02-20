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
from copy import deepcopy
from proboscis import asserts
from fuelweb_test import logger
from fuelweb_test.helpers.decorators import log_snapshot_after_test
from fuelweb_test.settings import CONTRAIL_PLUGIN_PACK_UB_PATH
from fuelweb_test.tests.base_test_case import SetupEnvironment
from fuelweb_test.tests.base_test_case import TestBasic
from fuelweb_test.tests.test_jumbo_frames import TestJumboFrames
from helpers import vsrx
from helpers import plugin
from helpers import openstack
from helpers import settings
from tests.test_contrail_check import TestContrailCheck


@test(groups=["plugins"])
class IntegrationTests(TestBasic):
    """IntegrationTests."""

    pack_copy_path = '/var/www/nailgun/plugins/contrail-5.1'
    add_package = \
        '/var/www/nailgun/plugins/contrail-5.1/' \
        'repositories/ubuntu/contrail-setup*'
    ostf_msg = 'OSTF tests passed successfully.'

    cluster_id = ''

    pack_path = CONTRAIL_PLUGIN_PACK_UB_PATH

    CONTRAIL_DISTRIBUTION = os.environ.get('CONTRAIL_DISTRIBUTION')

    @test(depends_on=[SetupEnvironment.prepare_slaves_9],
          groups=["contrail_ha", "contrail_integration_tests"])
    @log_snapshot_after_test
    def contrail_ha(self):
        """Check Contrail deploy on HA environment.

        Scenario:
            1. Create an environment with "Neutron with tunneling
               segmentation" as a network configuration and CEPH storage
            2. Enable and configure Contrail plugin
            3. Add 3 nodes with controller role
            4. Add 3 nodes with "compute" and "Ceph-OSD" roles
            5. Add a node with contrail-controller role
            6. Add a node with contrail-analytics role
            7. Add a node with contrail-analytics-db role
            8. Deploy cluster with plugin
            9. Run contrail health check tests
            10. Run OSTF tests

        Duration 120 min

        """
        self.show_step(1)
        plugin.prepare_contrail_plugin(self, slaves=9,
                                       options={'images_ceph': True,
                                                'volumes_ceph': True,
                                                'ephemeral_ceph': True,
                                                'objects_ceph': True,
                                                'volumes_lvm': False})

        self.show_step(2)
        plugin.activate_plugin(self)
        # activate vSRX image
        vsrx_setup_result = vsrx.activate()

        plugin.show_range(self, 3, 8)
        self.fuel_web.update_nodes(
            self.cluster_id,
            {
                'slave-01': ['controller'],
                'slave-02': ['controller'],
                'slave-03': ['controller'],
                'slave-04': ['compute', 'ceph-osd'],
                'slave-05': ['compute', 'ceph-osd'],
                'slave-06': ['compute', 'ceph-osd'],
                'slave-07': ['contrail-controller'],
                'slave-08': ['contrail-analytics'],
                'slave-09': ['contrail-analytics-db']
            })

        self.show_step(8)
        openstack.deploy_cluster(self)
        self.show_step(9)
        TestContrailCheck(self).cloud_check(['contrail'])
        self.show_step(10)
        if vsrx_setup_result:
            self.fuel_web.run_ostf(cluster_id=self.cluster_id,
                                   test_sets=['smoke', 'sanity', 'ha'])

    @test(depends_on=[SetupEnvironment.prepare_slaves_9],
          groups=["contrail_ha_baseos", "contrail_integration_tests"])
    @log_snapshot_after_test
    def contrail_ha_baseos(self):
        """Check deploy HA-contrail on an environment with a base-os node.

        Scenario:
            1. Create an environment with "Neutron with tunneling
               segmentation" as a network configuration
            2. Enable and configure Contrail plugin
            3. Add a node with controller role
            4. Add 2 nodes with "compute" and "Storage-cinder" roles
            5. Add a node with Base-OS role
            6. Add a node with 'contrail-controller',
               "contrail-analytics" roles
            7. Add a node with "contrail-analytics","contrail-analytics-db"
               role
            8. Deploy cluster with plugin
            9. Run contrail health check tests
            10. Run OSTF tests

        Duration 120 min

        """
        self.show_step(1)
        plugin.prepare_contrail_plugin(self, slaves=9)

        self.show_step(2)
        plugin.activate_plugin(self)
        # activate vSRX image
        vsrx_setup_result = vsrx.activate()

        plugin.show_range(self, 3, 8)
        self.fuel_web.update_nodes(
            self.cluster_id,
            {
                'slave-01': ['controller'],
                'slave-02': ['compute', 'cinder'],
                'slave-03': ['compute', 'cinder'],
                'slave-04': ['base-os'],
                'slave-05': ['contrail-controller', 'contrail-analytics'],
                'slave-06': ['contrail-analytics-db', 'contrail-analytics'],
            })

        self.show_step(8)
        openstack.deploy_cluster(self)
        self.show_step(9)
        TestContrailCheck(self).cloud_check(['contrail'])
        self.show_step(10)
        if vsrx_setup_result:
            self.fuel_web.run_ostf(cluster_id=self.cluster_id)

    @test(depends_on=[SetupEnvironment.prepare_slaves_9],
          groups=["contrail_ceilometer", "contrail_integration_tests"])
    @log_snapshot_after_test
    def contrail_ceilometer(self):
        """Check deploy environment with Contrail and Ceilometer.

        Scenario:
            1. Create an environment with "Neutron with tunneling
               segmentation" as a network configuration and CEPH storage
            2. Enable and configure Contrail plugin
            3. Add a node with "controller" role
            4. Add a node with "controller" + "MongoDB" multirole
            5. Add a node with "controller"+ "ceph-OSD" multiroles
            6. Add a node with "compute" + "ceph-OSD" + "cinder" multiroles
            7. Add a node with "compute" + "ceph-OSD" multiroles
            8. Add a node with "MongoDB" role
            9. Add a node with 'contrail-controller' role
            10. Add a node with "contrail-analytics-db" and
               "contrail-analytics"  roles
            11. Deploy cluster with plugin
            12. Run contrail health check tests
            13. Run OSTF tests

        Duration 120 min

        """
        min_slave_ram = 10000
        self.show_step(1)
        plugin.prepare_contrail_plugin(
            self,
            slaves=9,
            options={'images_ceph': True,
                     'ceilometer': True})

        self.show_step(2)
        plugin.activate_plugin(self)
        # activate vSRX image
        vsrx_setup_result = vsrx.activate()

        plugin.show_range(self, 3, 11)
        self.fuel_web.update_nodes(
            self.cluster_id,
            {
                'slave-01': ['controller'],
                'slave-02': ['controller', 'ceph-osd'],
                'slave-03': ['controller', 'mongo'],
                'slave-04': ['compute', 'ceph-osd'],
                'slave-05': ['compute', 'ceph-osd', 'cinder'],
                'slave-06': ['mongo'],
                'slave-07': ['contrail-controller'],
                'slave-08': ['contrail-analytics-db', 'contrail-analytics']

            })
        self.show_step(11)
        openstack.deploy_cluster(self)
        self.show_step(12)
        TestContrailCheck(self).cloud_check(['contrail'])
        self.show_step(13)
        check_ram_result = openstack.check_slave_memory(min_slave_ram)
        # https://bugs.launchpad.net/fuel/newton/+bug/1584190
        # remove should fail, when bug will be fixed
        if vsrx_setup_result and check_ram_result:
            self.fuel_web.run_ostf(
                cluster_id=self.cluster_id,
                test_sets=['smoke', 'sanity', 'ha', 'tests_platform'],
                timeout=settings.OSTF_RUN_TIMEOUT,
                should_fail=1,
                failed_test_name=['Check stack autoscaling'])
        elif vsrx_setup_result:
            logger.warning('Ostf tests will be run without platform tests')
            self.fuel_web.run_ostf(
                cluster_id=self.cluster_id,
                test_sets=['smoke', 'sanity', 'ha'],
                timeout=settings.OSTF_RUN_TIMEOUT)

    @test(depends_on=[SetupEnvironment.prepare_slaves_5],
          groups=["contrail_jumbo", "contrail_integration_tests"])
    @log_snapshot_after_test
    def contrail_jumbo(self):
        """Check deploy contrail on an environment with jumbo-frames support.

        Scenario:
            1. Create an environment with "Neutron with tunneling
               segmentation" as a network configuration
            2. Enable and configure Contrail plugin
            3. Add a node with "controller" and "Ceph OSD" roles
            4. Add 2 nodes with "compute" and "Storage-Ceph OSD" roles
            5. Add a node with "contrail-analytics",
               'contrail-controller' roles
            6. Add node with "contrail-analytics-db" role
            7. Configure MTU on network interfaces (Jumbo-frames)
            8. Deploy cluster with plugin
            9. Run contrail health check tests
            10. Run OSTF tests

        Duration 120 min

        """
        self.show_step(1)
        plugin.prepare_contrail_plugin(
            self, slaves=5, options={'images_ceph': True}
        )

        jumbo = TestJumboFrames()

        devops_env = self.env.d_env
        private_bridge = devops_env.get_network(name='private').bridge_name()
        logger.info("Search for {0} interfaces for update".
                    format(private_bridge))

        # find private bridge interface
        bridge_interfaces = jumbo.get_host_bridge_ifaces(private_bridge)
        logger.info("Found {0} interfaces for update: {1}"
                    .format(len(bridge_interfaces), bridge_interfaces))

        # set MTU 9000 to private bridge interface
        for iface in bridge_interfaces:
            jumbo.set_host_iface_mtu(iface, 9000)
            logger.info("MTU of {0} was changed to 9000".format(iface))
            logger.debug("New {0} interface properties:\n{1}"
                         .format(iface, jumbo.get_host_iface(iface)))

        self.show_step(2)
        plugin.activate_plugin(self)

        interfaces = {
            'enp0s3': ['fuelweb_admin'],
            'enp0s4': ['public'],
            'enp0s5': ['management'],
            'enp0s6': ['private'],
            'enp0s7': ['storage'],
        }

        interfaces_update = [{
            'name': 'enp0s6',
            'interface_properties': {
                'mtu': 9000,
                'disable_offloading': False
            },
        }]

        # activate vSRX image
        vsrx_setup_result = vsrx.activate()

        plugin.show_range(self, 3, 7)
        self.fuel_web.update_nodes(
            self.cluster_id,
            {
                'slave-01': ['controller', 'ceph-osd'],
                'slave-02': ['compute', 'ceph-osd'],
                'slave-03': ['compute', 'ceph-osd'],
                'slave-04': ['contrail-controller', 'contrail-analytics'],
                'slave-05': ['contrail-analytics-db'],
            }
        )

        self.show_step(7)
        slave_nodes = \
            self.fuel_web.client.list_cluster_nodes(self.cluster_id)
        for node in slave_nodes:
            self.fuel_web.update_node_networks(
                node['id'], interfaces,
                override_ifaces_params=interfaces_update)

        self.show_step(8)
        openstack.deploy_cluster(self)
        self.show_step(9)
        TestContrailCheck(self).cloud_check(['contrail'])
        self.show_step(10)
        if vsrx_setup_result:
            self.fuel_web.run_ostf(cluster_id=self.cluster_id)

        for node_name in ['slave-01', 'slave-02',
                          'slave-03', 'slave-04', 'slave-05']:
            node = self.fuel_web.get_nailgun_node_by_name(node_name)
            with self.env.d_env.get_ssh_to_remote(node['ip']) as remote:
                asserts.assert_true(
                    jumbo.check_node_iface_mtu(remote, "enp0s6", 9000),
                    "MTU on {0} is not 9000. Actual value: {1}"
                    .format(remote.host,
                            jumbo.get_node_iface(remote, "enp0s6")))

    @test(depends_on=[SetupEnvironment.prepare_slaves_9],
          groups=["contrail_bonding", "contrail_integration_tests"])
    @log_snapshot_after_test
    def contrail_bonding(self):
        """Check deploy contrail with aggregation of network interfaces.

        Scenario:
            1. Create an environment with "Neutron with tunneling
               segmentation" as a network configuration
            2. Enable and configure Contrail plugin
            3. Add 3 nodes with controller role
            4. Add 2 nodes with "compute" roles
            5. Add a node with 'contrail-controller' role
            6. Add a node with "contrail-analytics" role
            7. Add 2 nodes with "contrail-analytics-db" role
            8. Bond network interfaces with balance-rr mode
            9. Deploy cluster with plugin
            10. Run contrail health check tests
            11. Run OSTF tests

        Duration 120 min

        """
        self.show_step(1)
        plugin.prepare_contrail_plugin(self, slaves=9)

        self.show_step(2)
        plugin.activate_plugin(self)

        # configure vlan on storage and private interfaces
        openstack.assign_vlan(self, private=101, storage=102)

        plugin.show_range(self, 3, 8)
        self.fuel_web.update_nodes(
            self.cluster_id,
            {
                'slave-01': ['controller'],
                'slave-02': ['controller'],
                'slave-03': ['controller'],
                'slave-04': ['compute'],
                'slave-05': ['compute'],
                'slave-06': ['contrail-controller'],
                'slave-07': ['contrail-analytics'],
                'slave-08': ['contrail-analytics-db'],
                'slave-09': ['contrail-analytics-db'],
            },
        )

        cluster_nodes = self.fuel_web.client.list_cluster_nodes(
            self.cluster_id)

        self.show_step(8)
        for node in cluster_nodes:
            self.fuel_web.update_node_networks(
                node['id'],
                interfaces_dict=deepcopy(plugin.INTERFACES),
                raw_data=deepcopy(plugin.BOND_CONFIG))

        self.show_step(9)
        openstack.deploy_cluster(self)
        self.show_step(10)
        TestContrailCheck(self).cloud_check(['contrail'])

        # TODO(unknown)
        # Tests using north-south connectivity are expected to fail because
        # they require additional gateway nodes, and specific contrail
        # settings. This mark is a workaround until it's verified
        # and tested manually.
        # When it will be done 'should_fail=2' and
        # 'failed_test_name' parameter should be removed.

        self.show_step(11)
        self.fuel_web.run_ostf(
            cluster_id=self.cluster_id,
            test_sets=['smoke', 'sanity', 'ha'],
            timeout=45 * 60,
            should_fail=2,
            failed_test_name=[('Check network connectivity '
                               'from instance via floating IP'),
                              ('Launch instance with file injection')]
        )

    @test(depends_on=[SetupEnvironment.prepare_slaves_9],
          groups=["contrail_vlan", "contrail_integration_tests"])
    @log_snapshot_after_test
    def contrail_vlan(self):
        """Check deploy contrail on an environment with vlan-tagging.

        Scenario:
            1. Create an environment with "Neutron with tunneling
               segmentation" as a network configuration
            2. Enable and configure Contrail plugin
            3. Configure VLAN on network interfaces
            4. Add 3 nodes with controller role
            5. Add 2 nodes with "compute" and "Storage-cinder" roles
            6. Add 2 nodes with 'contrail-controller' role
            7. Add a node with "contrail-analytics" role
            8. Add a node with 'contrail-analytics-db' role
            9. Deploy cluster with plugin
            10. Run contrail health check tests
            11. Run OSTF tests

        Duration 120 min

        """
        self.show_step(1)
        plugin.prepare_contrail_plugin(self, slaves=9)

        self.show_step(2)
        plugin.activate_plugin(self)

        self.show_step(3)
        openstack.assign_vlan(self, storage=101, management=102)

        # activate vSRX image
        vsrx_setup_result = vsrx.activate()

        plugin.show_range(self, 4, 9)
        self.fuel_web.update_nodes(
            self.cluster_id,
            {
                'slave-01': ['controller'],
                'slave-02': ['controller'],
                'slave-03': ['controller'],
                'slave-04': ['compute', 'cinder'],
                'slave-05': ['compute', 'cinder'],
                'slave-06': ['contrail-controller'],
                'slave-07': ['contrail-controller'],
                'slave-08': ['contrail-analytics'],
                'slave-09': ['contrail-analytics-db']
            })

        self.show_step(9)
        openstack.deploy_cluster(self)
        self.show_step(10)
        TestContrailCheck(self).cloud_check(['contrail'])

        self.show_step(11)
        if vsrx_setup_result:
            self.fuel_web.run_ostf(
                cluster_id=self.cluster_id,
                test_sets=['smoke', 'sanity', 'ha'])

    @test(depends_on=[SetupEnvironment.prepare_slaves_9],
          groups=["contrail_ceph_multirole", "contrail_integration_tests"])
    @log_snapshot_after_test
    def contrail_ceph_multirole(self):
        """Check deploy contrail with Controller + Ceph multirole.

        Scenario:
            1. Create an environment with "Neutron with tunneling
               segmentation" as a network configuration and CEPH storage
            2. Enable and configure Contrail plugin
            3. Add 3 nodes with "controller" + "Ceph-OSD" multirole
            4. Add 2 nodes with "compute" role
            5. Add a node with 'contrail-controller' role
            6. Add 2 nodes with 'contrail-analytics-db',
               "contrail-analytics" roles
            7. Add a node with 'contrail-analytics-db' role
            8. Deploy cluster with plugin
            9. Run contrail health check tests
            10. Run OSTF tests

        """
        self.show_step(1)
        plugin.prepare_contrail_plugin(
            self, slaves=9,
            options={
                'images_ceph': True,
                'volumes_ceph': True,
                'ephemeral_ceph': True,
                'objects_ceph': True,
                'volumes_lvm': False
            })

        self.show_step(2)
        plugin.activate_plugin(self)

        # activate vSRX image
        vsrx_setup_result = vsrx.activate()

        plugin.show_range(self, 3, 8)
        self.fuel_web.update_nodes(
            self.cluster_id,
            {
                'slave-01': ['controller', 'ceph-osd'],
                'slave-02': ['controller', 'ceph-osd'],
                'slave-03': ['controller', 'ceph-osd'],
                'slave-04': ['compute'],
                'slave-05': ['compute'],
                'slave-06': ['contrail-controller'],
                'slave-07': ['contrail-analytics-db', 'contrail-analytics'],
                'slave-08': ['contrail-analytics-db', 'contrail-analytics'],
                'slave-09': ['contrail-analytics-db']
            })

        self.show_step(8)
        openstack.deploy_cluster(self)
        self.show_step(9)
        TestContrailCheck(self).cloud_check(['contrail'])

        self.show_step(10)
        if vsrx_setup_result:
            self.fuel_web.run_ostf(cluster_id=self.cluster_id,
                                   test_sets=['smoke', 'sanity', 'ha'])

    @test(depends_on=[SetupEnvironment.prepare_slaves_9],
          groups=["contrail_cinder_multirole", "contrail_integration_tests"])
    @log_snapshot_after_test
    def contrail_cinder_multirole(self):
        """Check deploy contrail with Controller + Cinder multirole.

        Scenario:
            1. Create an environment with "Neutron with tunneling
               segmentation" as a network configuration
            2. Enable and configure Contrail plugin
            3. Add 3 nodes with "controller" + "storage-cinder" multirole
            4. Add 2 nodes with "compute" role
            5. Add 2 node with 'contrail-controller',
               "contrail-analytics" roles
            6. Add a node with 'contrail-analytics-db' role
            7. Deploy cluster with plugin
            8. Run contrail health check tests
            9. Run OSTF tests

        """
        self.show_step(1)
        plugin.prepare_contrail_plugin(self, slaves=9)

        self.show_step(2)
        plugin.activate_plugin(self)

        # activate vSRX image
        vsrx_setup_result = vsrx.activate()

        plugin.show_range(self, 3, 7)
        self.fuel_web.update_nodes(
            self.cluster_id,
            {
                'slave-01': ['controller', 'cinder'],
                'slave-02': ['controller', 'cinder'],
                'slave-03': ['controller', 'cinder'],
                'slave-04': ['compute'],
                'slave-05': ['compute'],
                'slave-06': ['contrail-controller', 'contrail-analytics'],
                'slave-07': ['contrail-analytics', 'contrail-controller'],
                'slave-08': ['contrail-analytics-db']
            })

        self.show_step(7)
        openstack.deploy_cluster(self)
        self.show_step(8)
        TestContrailCheck(self).cloud_check(['contrail'])

        self.show_step(9)
        if vsrx_setup_result:
            self.fuel_web.run_ostf(cluster_id=self.cluster_id,
                                   test_sets=['smoke', 'sanity', 'ha'])

    @test(depends_on=[SetupEnvironment.prepare_slaves_9],
          groups=["contrail_cinder_ceph_multirole",
                  "contrail_integration_tests"])
    @log_snapshot_after_test
    def contrail_cinder_ceph_multirole(self):
        """Check deploy contrail with Controller + Cinder + Ceph multirole.

        Scenario:
            1. Create an environment with "Neutron with tunneling
                segmentation" as a network configuration and CEPH storage
            2. Enable and configure Contrail plugin
            3. Add 1 node with "controller", "storage-cinder",
                and "Ceph-OSD" roles
            4. Add 1 node with "controller" + "storage-cinder" and 1 node
                with "controller" + "Ceph-OSD" multiroles
            5. Add 1 nodes with "compute", "cinder", "ceph-osd" roles
            6. Add 1 nodes with "compute" role
            7. Add a node with 'contrail-controller' role
            8. Add 2 node with 'contrail-analytics-db',
               "contrail-analytics" roles
            9. Add a node with 'contrail-analytics-db' role
            10. Deploy cluster with plugin
            11. Run contrail health check tests
            12. Run OSTF tests

        """
        self.show_step(1)
        plugin.prepare_contrail_plugin(
            self, slaves=9, options={'images_ceph': True}
        )

        self.show_step(2)
        plugin.activate_plugin(self)

        # activate vSRX image
        vsrx_setup_result = vsrx.activate()

        plugin.show_range(self, 3, 10)
        self.fuel_web.update_nodes(
            self.cluster_id,
            {
                'slave-01': ['controller', 'cinder', 'ceph-osd'],
                'slave-02': ['controller', 'cinder'],
                'slave-03': ['controller', 'ceph-osd'],
                'slave-04': ['compute', 'cinder', 'ceph-osd'],
                'slave-05': ['compute'],
                'slave-06': ['contrail-controller'],
                'slave-07': ['contrail-analytics-db', 'contrail-analytics'],
                'slave-08': ['contrail-analytics-db', 'contrail-analytics'],
                'slave-09': ['contrail-analytics-db']
            })

        self.show_step(10)
        openstack.deploy_cluster(self)
        self.show_step(11)
        TestContrailCheck(self).cloud_check(['contrail'])

        self.show_step(12)
        if vsrx_setup_result:
            self.fuel_web.run_ostf(cluster_id=self.cluster_id,
                                   test_sets=['smoke', 'sanity', 'ha'])

    @test(depends_on=[SetupEnvironment.prepare_slaves_5],
          groups=["contrail_update_core_repos"])
    @log_snapshot_after_test
    def contrail_update_core_repos(self):
        """Check updating core repos with Contrail plugin.

        Scenario:
            1. Deploy cluster with Contrail plugin
            2. Run 'fuel-mirror create -P ubuntu -G mos ubuntu'
               on the master node
            3. Run 'fuel-mirror apply -P ubuntu -G mos ubuntu
               --env <env_id> --replace' on the master node
            4. Update repos for all deployed nodes with command
               "fuel --env <env_id> node --node-id 1,2,3,4,5,6,7,9,10
               --tasks setup_repositories" on the master node
            5. Run OSTF and check Contrail node status.

        """
        self.show_step(1)
        plugin.prepare_contrail_plugin(self, slaves=5)
        plugin.activate_plugin(self)
        vsrx_setup_result = vsrx.activate()
        conf_nodes = {
            'slave-01': ['controller'],
            'slave-02': ['compute', 'cinder'],
            'slave-03': ['contrail-controller'],
            'slave-04': ['contrail-analytics'],
            'slave-05': ['contrail-analytics-db']
        }
        self.fuel_web.update_nodes(self.cluster_id, conf_nodes)
        openstack.deploy_cluster(self)

        plugin.show_range(self, 2, 5)

        nodes = self.fuel_web.client.list_cluster_nodes(self.cluster_id)
        node_ids = ','.join([str(node['id']) for node in nodes])
        commands = [
            'fuel-mirror create -P ubuntu -G mos ubuntu',
            ('fuel-mirror apply -P ubuntu -G mos ubuntu '
             '--env {0} --replace'.format(self.cluster_id)),
            ('fuel --env {0} node --node-id {1} '
             '--tasks setup_repositories'.format(self.cluster_id, node_ids))
        ]
        for cmd in commands:
            logger.info("Execute commmand: '{0}' om master node.".format(cmd))
            result = self.env.d_env.get_admin_remote().execute(cmd)
            asserts.assert_equal(
                result['exit_code'], 0,
                'Command "{0}" fails with message: "{1}".'.format(
                    cmd, result['stderr']))
        if vsrx_setup_result:
            self.show_step(5)
            self.fuel_web.run_ostf(cluster_id=self.cluster_id)
            TestContrailCheck(self).cloud_check(['contrail'])

    @test(depends_on=[SetupEnvironment.prepare_slaves_9],
          groups=["contrail_sahara", "contrail_integration_tests"])
    @log_snapshot_after_test
    def contrail_sahara(self):
        """Check Contrail deploy with sahara.

        Scenario:
            1. Create an environment with "Neutron with tunneling
               segmentation" as a network configuration and CEPH storage
            2. Enable sahara
            3. Enable and configure Contrail plugin
            4. Add a node with controller role
            5. Add 3 nodes with "compute" and "Ceph-OSD" roles
            6. Add a node with contrail-controller role
            7. Add a node with 'contrail-analytics' role
            8. Add a node with 'contrail-analytics-db' role
            9. Deploy cluster with plugin
            10. Run contrail health check tests
            11. Run OSTF tests

        Duration 120 min

        """
        min_slave_ram = 8138

        plugin.show_range(self, 1, 3)
        plugin.prepare_contrail_plugin(self, slaves=9,
                                       options={'images_ceph': True,
                                                'volumes_ceph': True,
                                                'ephemeral_ceph': True,
                                                'objects_ceph': True,
                                                'volumes_lvm': False,
                                                'sahara': True})

        self.show_step(3)
        plugin.activate_plugin(self)
        # activate vSRX image
        vsrx_setup_result = vsrx.activate()

        plugin.show_range(self, 4, 9)
        self.fuel_web.update_nodes(
            self.cluster_id,
            {
                'slave-01': ['controller'],
                'slave-02': ['compute', 'ceph-osd'],
                'slave-03': ['compute', 'ceph-osd'],
                'slave-04': ['compute', 'ceph-osd'],
                'slave-05': ['contrail-controller'],
                'slave-06': ['contrail-analytics-db'],
                'slave-07': ['contrail-analytics']
            })

        self.show_step(9)
        openstack.deploy_cluster(self)
        self.show_step(10)
        TestContrailCheck(self).cloud_check(['contrail'])
        self.show_step(11)
        check_ram_result = openstack.check_slave_memory(min_slave_ram)
        if vsrx_setup_result and check_ram_result:
            self.fuel_web.run_ostf(
                cluster_id=self.cluster_id,
                test_sets=['smoke', 'sanity', 'tests_platform'],
                timeout=settings.OSTF_RUN_TIMEOUT
                )
        elif vsrx_setup_result:
            logger.warning('Ostf tests will be run without platform tests')
            self.fuel_web.run_ostf(
                cluster_id=self.cluster_id,
                test_sets=['smoke', 'sanity'],
                timeout=settings.OSTF_RUN_TIMEOUT
            )

    @test(depends_on=[SetupEnvironment.prepare_slaves_5],
          groups=["contrail_murano", "contrail_integration_tests"])
    @log_snapshot_after_test
    def contrail_murano(self):
        """Check deploy contrail with murano.

        Scenario:
            1. Create an environment with "Neutron with tunneling
               segmentation" as a network configuration
            2. Enable murano
            3. Enable and configure Contrail plugin
            4. Add a node with controller role
            5. Add a node with "compute" and "Storage-cinder" roles
            6. Add a node with 'contrail-controller' role
            7. Add a node with "contrail-analytics" role
            8. Add a node with "contrail-analytics-db" role
            9. Deploy cluster with plugin
            10. Run contrail health check tests
            11. Run OSTF tests

        Duration 120 min

        """
        min_slave_ram = 10000

        plugin.show_range(self, 1, 3)
        plugin.prepare_contrail_plugin(self, slaves=5,
                                       options={'murano': True})

        self.show_step(3)
        plugin.activate_plugin(self, contrail_api_public_port="8098")

        # activate vSRX image
        vsrx_setup_result = vsrx.activate()

        plugin.show_range(self, 4, 9)
        self.fuel_web.update_nodes(
            self.cluster_id,
            {
                'slave-01': ['controller'],
                'slave-02': ['compute', 'cinder'],
                'slave-03': ['contrail-controller'],
                'slave-04': ['contrail-analytics'],
                'slave-05': ['contrail-analytics-db']
            })

        self.show_step(9)
        openstack.deploy_cluster(self)
        self.show_step(10)
        TestContrailCheck(self).cloud_check(['contrail'])

        self.show_step(11)
        check_ram_result = openstack.check_slave_memory(min_slave_ram)
        if vsrx_setup_result and check_ram_result:
            self.fuel_web.run_ostf(
                cluster_id=self.cluster_id,
                test_sets=['smoke', 'sanity', 'tests_platform'],
                timeout=settings.OSTF_RUN_TIMEOUT
                )
        elif vsrx_setup_result:
            logger.warning('Ostf tests will be run without platform tests')
            self.fuel_web.run_ostf(
                cluster_id=self.cluster_id,
                test_sets=['smoke', 'sanity'],
                timeout=settings.OSTF_RUN_TIMEOUT
                )
