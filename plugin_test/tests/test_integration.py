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
            6. Add 3 nodes with "contrail-config", "contrail-control" and "contrail-db" roles
            7. Deploy cluster with plugin
            8. Run OSTF tests

        Duration 120 min

        """
        plugin.prepare_contrail_plugin(self, slaves=9)

        # enable plugin in contrail settings
        plugin.activate_plugin(self)

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

        self.fuel_web.run_ostf(
            cluster_id=self.cluster_id,
            should_fail=2,
            failed_test_name=[('Check network connectivity '
                               'from instance via floating IP'),
                              ('Launch instance with file injection')]
        )

    @test(depends_on=[SetupEnvironment.prepare_slaves_9],
          groups=["contrail_ceilometer"])
    @log_snapshot_after_test
    def contrail_ceilometer(self):
        """Check deploy environment with Contrail and Ceilometer

        Scenario:
            1. Create an environment with "Neutron with tunneling segmentation"
               as a network configuration and CEPH storage
            2. Enable and configure Contrail plugin
            3. Add 3 nodes with controller role
            4. Add 2 nodes with "compute" and "Ceph-OSD" roles
            5. Add a node with MongoDB role
            6. Add a node with "contrail-config", "contrail-control" and "contrail-db" roles
            7. Deploy cluster with plugin
            8. Run OSTF tests

        Duration 120 min

        """
        plugin.prepare_contrail_plugin(self, slaves=9, ceph_value=True)

        # enable plugin in contrail settings
        plugin.activate_plugin(self)

        self.fuel_web.update_nodes(
            self.cluster_id,
            {
                'slave-01': ['controller'],
                'slave-02': ['controller'],
                'slave-03': ['controller'],
                'slave-04': ['compute', 'ceph-osd'],
                'slave-05': ['compute', 'ceph-osd'],
                'slave-06': ['mongo'],
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

        self.fuel_web.run_ostf(
            cluster_id=self.cluster_id,
            test_sets=['smoke', 'sanity', 'ha', 'tests_platform'],
            should_fail=2,
            failed_test_name=[('Check network connectivity '
                               'from instance via floating IP'),
                              ('Launch instance with file injection')]
        )
