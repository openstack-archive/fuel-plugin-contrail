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
from proboscis import test
from copy import deepcopy
from proboscis import asserts
from fuelweb_test import logger
from fuelweb_test.helpers.decorators import log_snapshot_after_test
from fuelweb_test.settings import CONTRAIL_PLUGIN_PACK_UB_PATH
from fuelweb_test.tests.base_test_case import SetupEnvironment
from fuelweb_test.tests.base_test_case import TestBasic
from fuelweb_test.tests.test_jumbo_frames import TestJumboFrames
from helpers import plugin
from helpers import openstack


@test(groups=["plugins"])
class IntegrationTests(TestBasic):
    """IntegrationTests."""

    pack_copy_path = '/var/www/nailgun/plugins/contrail-3.0'
    add_package = \
        '/var/www/nailgun/plugins/contrail-3.0/' \
        'repositories/ubuntu/contrail-setup*'
    ostf_msg = 'OSTF tests passed successfully.'

    cluster_id = ''

    pack_path = CONTRAIL_PLUGIN_PACK_UB_PATH

    CONTRAIL_DISTRIBUTION = os.environ.get('CONTRAIL_DISTRIBUTION')

    @test(depends_on=[SetupEnvironment.prepare_slaves_9],
          groups=["contrail_ha"])
    @log_snapshot_after_test
    def contrail_ha(self):
        """Check Contrail deploy on HA environment

        Scenario:
            1. Create an environment with "Neutron with tunneling segmentation"
               as a network configuration and CEPH storage
            2. Enable and configure Contrail plugin
            3. Add 3 nodes with controller role
            4. Add 2 nodes with "compute" and "Ceph-OSD" roles
            5. Add a node with contrail-config role
            6. Add a node with contrail-control role
            7. Add a node with contrail-db role
            8. Deploy cluster with plugin
            9. Run OSTF tests

        Duration 120 min

        """
        plugin.prepare_contrail_plugin(self, slaves=9, ceph_value=True)

        # enable plugin in contrail settings
        plugin.activate_plugin(self)
        # activate vSRX image
        plugin.activate_vsrx()

        self.fuel_web.update_nodes(
            self.cluster_id,
            {
                'slave-01': ['controller'],
                'slave-02': ['controller'],
                'slave-03': ['controller'],
                'slave-04': ['compute', 'ceph-osd'],
                'slave-05': ['compute', 'ceph-osd'],
                'slave-06': ['contrail-config'],
                'slave-07': ['contrail-control'],
                'slave-08': ['contrail-db'],
            })

        # deploy cluster
        openstack.deploy_cluster(self)

        self.fuel_web.run_ostf(cluster_id=self.cluster_id)

    @test(depends_on=[SetupEnvironment.prepare_slaves_9],
          groups=["contrail_ha_baseos"])
    @log_snapshot_after_test
    def contrail_ha_baseos(self):
        """Check deploy HA-contrail on an environment with a base-os node

        Scenario:
            1. Create an environment with "Neutron with tunneling segmentation"
               as a network configuration
            2. Enable and configure Contrail plugin
            3. Add a node with controller role
            4. Add 2 nodes with "compute" and "Storage-cinder" roles
            5. Add a node with Base-OS role
            6. Add 3 nodes with "contrail-config", "contrail-control" and
             "contrail-db" roles
            7. Deploy cluster with plugin
            8. Run OSTF tests

        Duration 120 min

        """
        plugin.prepare_contrail_plugin(self, slaves=9)

        # enable plugin in contrail settings
        plugin.activate_plugin(self)
        # activate vSRX image
        plugin.activate_vsrx()

        self.fuel_web.update_nodes(
            self.cluster_id,
            {
                'slave-01': ['controller'],
                'slave-02': ['compute', 'cinder'],
                'slave-03': ['compute', 'cinder'],
                'slave-04': ['base-os'],
                'slave-05': ['contrail-config',
                             'contrail-control',
                             'contrail-db'],
                'slave-06': ['contrail-config',
                             'contrail-control',
                             'contrail-db'],
                'slave-07': ['contrail-config',
                             'contrail-control',
                             'contrail-db'],
            })

        # deploy cluster
        openstack.deploy_cluster(self)

        # TODO
        # Tests using north-south connectivity are expected to fail because
        # they require additional gateway nodes, and specific contrail
        # settings. This mark is a workaround until it's verified
        # and tested manually.
        # When it will be done 'should_fail=2' and
        # 'failed_test_name' parameter should be removed.

        self.fuel_web.run_ostf(cluster_id=self.cluster_id)

    @test(depends_on=[SetupEnvironment.prepare_slaves_9],
          groups=["contrail_ceilometer"])
    @log_snapshot_after_test
    def contrail_ceilometer(self):
        """Check deploy environment with Contrail and Ceilometer

        Scenario:
            1. Create an environment with "Neutron with tunneling segmentation"
               as a network configuration and CEPH storage
            2. Enable and configure Contrail plugin
            3. Add 2 nodes with "controller" role and 1 node with
               "controller" + "MongoDB" multirole
            4. Add 1 node with "compute" and "ceph-OSD" and
               1 node with "compute" + "ceph-OSD" + " MongoDB" multiroles
            5. Add a node with "MongoDB" role
            6. Add a node with "contrail-config", "contrail-control" and
               "contrail-db" roles
            7. Deploy cluster with plugin
            8. Run OSTF tests

        Duration 120 min

        """
        plugin.prepare_contrail_plugin(self, slaves=9, ceph_value=True)

        # enable plugin in contrail settings
        plugin.activate_plugin(self)
        # activate vSRX image
        plugin.activate_vsrx()

        self.fuel_web.update_nodes(
            self.cluster_id,
            {
                'slave-01': ['controller'],
                'slave-02': ['controller'],
                'slave-03': ['controller', 'mongo'],
                'slave-04': ['compute', 'ceph-osd', 'mongo'],
                'slave-05': ['compute', 'ceph-osd'],
                'slave-06': ['mongo'],
                'slave-07': ['contrail-config',
                             'contrail-control',
                             'contrail-db'],
            })
        # deploy cluster
        openstack.deploy_cluster(self)

        self.fuel_web.run_ostf(cluster_id=self.cluster_id)

    @test(depends_on=[SetupEnvironment.prepare_slaves_9],
          groups=["contrail_jumbo"])
    @log_snapshot_after_test
    def contrail_jumbo(self):
        """Check deploy contrail on an environment with jumbo-frames support

        Scenario:
            1. Create an environment with "Neutron with tunneling segmentation"
               as a network configuration
            2. Enable and configure Contrail plugin
            3. Add a node with controller role
            4. Add 2 nodes with "compute" and "Storage-Ceph OSD" roles
            5. Add a node with "contrail-config", "contrail-control" and
               "contrail-db" roles
            6. Add 2 nodes with "contrail-config", "contrail-control" roles
            7. Configure MTU on network interfaces (Jumbo-frames)
            8. Deploy cluster with plugin
            9. Run OSTF tests

        Duration 120 min

        """

        plugin.prepare_contrail_plugin(self, slaves=9, ceph_value=True)

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

        # enable plugin in contrail settings
        plugin.activate_plugin(self)

        interfaces = {
            'eth0': ['fuelweb_admin'],
            'eth1': ['public'],
            'eth2': ['management'],
            'eth3': ['private'],
            'eth4': ['storage'],
            }

        interfaces_update = [{
            'name': 'eth3',
            'interface_properties': {
                'mtu': 9000,
                'disable_offloading': False
            },
            }]

        # activate vSRX image
        plugin.activate_vsrx()

        self.fuel_web.update_nodes(
            self.cluster_id,
            {
                'slave-01': ['controller'],
                'slave-02': ['compute', 'ceph-osd'],
                'slave-03': ['compute', 'ceph-osd'],
                'slave-04': ['contrail-config',
                             'contrail-control',
                             'contrail-db'],
                'slave-05': ['contrail-config',
                             'contrail-control'],
                'slave-06': ['contrail-config',
                             'contrail-control'],
                })

        slave_nodes = self.fuel_web.client.list_cluster_nodes(self.cluster_id)
        for node in slave_nodes:
            self.fuel_web.update_node_networks(
                node['id'], interfaces,
                override_ifaces_params=interfaces_update)

        # deploy cluster
        openstack.deploy_cluster(self)

        self.fuel_web.run_ostf(cluster_id=self.cluster_id)

        for node_name in ['slave-01', 'slave-02',
                          'slave-03', 'slave-04', 'slave-05', 'slave-06']:
            node = self.fuel_web.get_nailgun_node_by_name(node_name)
            with self.env.d_env.get_ssh_to_remote(node['ip']) as remote:
                asserts.assert_true(
                    jumbo.check_node_iface_mtu(remote, "eth3", 9000),
                    "MTU on {0} is not 9000. Actual value: {1}"
                    .format(remote.host,
                            jumbo.get_node_iface(remote, "eth3")))

    @test(depends_on=[SetupEnvironment.prepare_slaves_9],
          groups=["contrail_bonding"])
    @log_snapshot_after_test
    def contrail_bonding(self):
        """Check deploy contrail with aggregation of network interfaces

        Scenario:
            1. Create an environment with "Neutron with tunneling segmentation"
               as a network configuration
            2. Enable and configure Contrail plugin
            3. Add 3 nodes with controller role
            4. Add 2 nodes with "compute" roles
            5. Add 3 nodes with "contrail-config", "contrail-control" and
               "contrail-db" roles
            8. Bond network interfaces with Active Backup mode
            9. Deploy cluster with plugin
            10. Run OSTF tests

        Duration 120 min

        """

        plugin.prepare_contrail_plugin(self, slaves=9)

        # enable plugin in contrail settings
        plugin.activate_plugin(self)

        self.fuel_web.update_nodes(
            self.cluster_id,
            {
                'slave-01': ['controller'],
                'slave-02': ['controller'],
                'slave-03': ['controller'],
                'slave-04': ['compute'],
                'slave-05': ['compute'],
                'slave-06': ['contrail-config',
                             'contrail-control',
                             'contrail-db'],
                'slave-07': ['contrail-config',
                             'contrail-control',
                             'contrail-db'],
                'slave-08': ['contrail-config',
                             'contrail-control',
                             'contrail-db'],
            },
            )

        cluster_nodes = \
            self.fuel_web.client.list_cluster_nodes(self.cluster_id)

        for node in cluster_nodes:
            self.fuel_web.update_node_networks(
                node['id'], interfaces_dict=deepcopy(plugin.INTERFACES),
                raw_data=deepcopy(plugin.BOND_CONFIG)
                )

        openstack.deploy_cluster(self)

        # TODO
        # Tests using north-south connectivity are expected to fail because
        # they require additional gateway nodes, and specific contrail
        # settings. This mark is a workaround until it's verified
        # and tested manually.
        # When it will be done 'should_fail=2' and
        # 'failed_test_name' parameter should be removed.

        self.fuel_web.run_ostf(
            cluster_id=self.cluster_id,
            test_sets=['smoke', 'sanity', 'ha', 'tests_platform'],
            should_fail=2,
            failed_test_name=[('Check network connectivity '
                               'from instance via floating IP'),
                              ('Launch instance with file injection')]
        )

    @test(depends_on=[SetupEnvironment.prepare_slaves_9],
          groups=["contrail_vlan"])
    @log_snapshot_after_test
    def contrail_vlan(self):
        """Check deploy contrail on an environment with vlan-tagging

        Scenario:
            1. Create an environment with "Neutron with tunneling segmentation"
               as a network configuration
            2. Enable and configure Contrail plugin
            3. Add 3 nodes with controller role
            4. Add 2 nodes with "compute" and "Storage-cinder" roles
            5. Add a node with "contrail-config" and "contrail-db" roles
            6. Add a node with "contrail-db", "contrail-control" roles
            7. Add a node with "contrail-db" role
            8. Configure VLAN on network interfaces
            9. Deploy cluster with plugin
            10. Run OSTF tests

        Duration 120 min

        """
        plugin.prepare_contrail_plugin(self, slaves=9)

        # enable plugin in contrail settings
        plugin.activate_plugin(self)

        # configure vlan on storage and management interfaces
        networking_parameters = self.fuel_web.client.get_networks(
            self.cluster_id)
        tags = {'storage': 101, 'management': 102}
        for name in networking_parameters["networks"]:
            for k in tags.keys():
                if k == str(name['name']):
                    name['vlan_start'] = tags[k]

        self.fuel_web.client.update_network(self.cluster_id)

        # activate vSRX image
        plugin.activate_vsrx()

        self.fuel_web.update_nodes(
            self.cluster_id,
            {
                'slave-01': ['controller'],
                'slave-02': ['controller'],
                'slave-03': ['controller'],
                'slave-04': ['compute', 'cinder'],
                'slave-05': ['compute', 'cinder'],
                'slave-06': ['contrail-config', 'contrail-db'],
                'slave-07': ['contrail-control', 'contrail-db'],
                'slave-08': ['contrail-db'],
            })

        # deploy cluster
        openstack.deploy_cluster(self)

        # TODO
        # Tests using north-south connectivity are expected to fail because
        # they require additional gateway nodes, and specific contrail
        # settings. This mark is a workaround until it's verified
        # and tested manually.
        # When it will be done 'should_fail=2' and
        # 'failed_test_name' parameter should be removed.

        self.fuel_web.run_ostf(
            cluster_id=self.cluster_id,
            test_sets=['smoke', 'sanity', 'ha', 'tests_platform'])

    @test(depends_on=[SetupEnvironment.prepare_slaves_9],
          groups=["contrail_ceph_multirole"])
    @log_snapshot_after_test
    def contrail_ceph_multirole(self):
        """Check deploy contrail with Controller + Ceph multirole

        Scenario:
            1. Create an environment with "Neutron with tunneling segmentation"
               as a network configuration and CEPH storage
            2. Enable and configure Contrail plugin
            3. Add 3 nodes with "controller" + "Ceph-OSD" multirole
            4. Add 2 nodes with "compute" role
            5. Add 1 node with "contrail-config", "contrail-control" and "contrail-db" roles
            6. Deploy cluster with plugin
            8. Run OSTF tests

        """

        plugin.prepare_contrail_plugin(self, slaves=9, ceph_value=True)

        # enable plugin in contrail settings
        plugin.activate_plugin(self)

        # activate vSRX image
        plugin.activate_vsrx()

        self.fuel_web.update_nodes(
            self.cluster_id,
            {
                'slave-01': ['controller', 'ceph-osd'],
                'slave-02': ['controller', 'ceph-osd'],
                'slave-03': ['controller', 'ceph-osd'],
                'slave-04': ['compute'],
                'slave-05': ['compute'],
                'slave-06': ['contrail-config', 'contrail-control', 'contrail-db'],
            })

        # deploy cluster
        openstack.deploy_cluster(self)

        # run OSTF tests
        self.fuel_web.run_ostf(cluster_id=self.cluster_id)

    @test(depends_on=[SetupEnvironment.prepare_slaves_9],
          groups=["contrail_cinder_multirole"])
    @log_snapshot_after_test
    def contrail_cinder_multirole(self):
        """Check deploy contrail with Controller + Cinder multirole

        Scenario:
            1. Create an environment with "Neutron with tunneling segmentation" as a network configuration
            2. Enable and configure Contrail plugin
            3. Add 3 nodes with "controller" + "storage-cinder" multirole
            4. Add 1 node with "compute" role
            5. Add 2 nodes with "contrail-config", "contrail-control" and "contrail-db" roles
            6. Deploy cluster with plugin
            8. Run OSTF tests

        """

        plugin.prepare_contrail_plugin(self, slaves=9)

        # enable plugin in contrail settings
        plugin.activate_plugin(self)

        # activate vSRX image
        plugin.activate_vsrx()

        self.fuel_web.update_nodes(
            self.cluster_id,
            {
                'slave-01': ['controller', 'cinder'],
                'slave-02': ['controller', 'cinder'],
                'slave-03': ['controller', 'cinder'],
                'slave-04': ['compute'],
                'slave-05': ['contrail-config', 'contrail-control', 'contrail-db'],
                'slave-06': ['contrail-config', 'contrail-control', 'contrail-db'],
            })

        # deploy cluster
        openstack.deploy_cluster(self)

        # run OSTF tests
        self.fuel_web.run_ostf(cluster_id=self.cluster_id)

    @test(depends_on=[SetupEnvironment.prepare_slaves_9],
          groups=["contrail_cinder_ceph_multirole"])
    @log_snapshot_after_test
    def contrail_cinder_ceph_multirole(self):
        """Check deploy contrail with Controller + Cinder + Ceph multirole

        Scenario:
            1. Create an environment with "Neutron with tunneling segmentation"
               as a network configuration and CEPH storage
            2. Enable and configure Contrail plugin
            3. Add 1 node with "controller" + "storage-cinder" + "Ceph-OSD" multirole
            4. Add 1 node with "controller" + "storage-cinder" and 1 node
               with "controller" + "Ceph-OSD" multiroles
            5. Add 2 nodes with "compute" role
            6. Add 3 nodes with "contrail-config", "contrail-control" and "contrail-db" roles
            7. Deploy cluster with plugin
            8. Run OSTF tests

        """

        plugin.prepare_contrail_plugin(self, slaves=9, ceph_value=True)

        # enable plugin in contrail settings
        plugin.activate_plugin(self)

        # activate vSRX image
        plugin.activate_vsrx()

        self.fuel_web.update_nodes(
            self.cluster_id,
            {
                'slave-01': ['controller', 'cinder', 'ceph-osd'],
                'slave-02': ['controller', 'cinder'],
                'slave-03': ['controller', 'ceph-osd'],
                'slave-04': ['compute'],
                'slave-05': ['compute'],
                'slave-06': ['contrail-config', 'contrail-control', 'contrail-db'],
                'slave-07': ['contrail-config', 'contrail-control', 'contrail-db'],
                'slave-08': ['contrail-config', 'contrail-control', 'contrail-db']
            })

        # deploy cluster
        openstack.deploy_cluster(self)

        # run OSTF tests
        self.fuel_web.run_ostf(cluster_id=self.cluster_id)
