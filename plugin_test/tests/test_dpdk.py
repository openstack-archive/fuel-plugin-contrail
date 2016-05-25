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
import functools
from proboscis import test
from proboscis.asserts import assert_equal
from fuelweb_test import logger
from fuelweb_test.helpers.decorators import log_snapshot_after_test
from fuelweb_test.settings import CONTRAIL_PLUGIN_PACK_UB_PATH
from fuelweb_test.tests.base_test_case import SetupEnvironment
from fuelweb_test.tests.base_test_case import TestBasic
from helpers import plugin
from helpers import openstack
from helpers import baremetal
from helpers import settings


def set_kvm_use(func):
    """ Set KVM_USE setting value to True
    which is necessary for DPDK tests
    """
    @functools.wraps(func)
    def wrapped(*args, **kwargs):
        from fuelweb_test import settings as fw_settings
        kvm_use_orig = fw_settings.KVM_USE
        fw_settings.KVM_USE = True
        response = func(*args, **kwargs)
        fw_settings.KVM_USE = kvm_use_orig
        return response
    return wrapped


@test(groups=["plugins"])
class DPDKTests(TestBasic):
    """DPDKTests."""

    pack_copy_path = '/var/www/nailgun/plugins/contrail-3.0'
    add_package = '/var/www/nailgun/plugins/contrail-3.0/'\
                  'repositories/ubuntu/contrail-setup*'
    ostf_msg = 'OSTF tests passed successfully.'
    cluster_id = ''
    pack_path = CONTRAIL_PLUGIN_PACK_UB_PATH
    CONTRAIL_DISTRIBUTION = os.environ.get('CONTRAIL_DISTRIBUTION')
    bm_drv = baremetal.BMDriver()

    @test(groups=["contrail_dpdk_setup"])
    @set_kvm_use
    def contrail_dpdk_setup(self):
        logger.info('[contrail_dpdk_setup]')
        self.bm_drv.host_prepare(self)
        self.bm_drv.setup_fuel_node(self,
                                    cluster_id=self.cluster_id,
                                    roles=['compute', 'ceph-osd', 'dpdk'])


    @test(depends_on=[SetupEnvironment.prepare_slaves_9],
          groups=["contrail_ha_dpdk"])
    @log_snapshot_after_test
    @set_kvm_use
    def contrail_ha_dpdk(self):
        """Check Contrail deploy on HA environment

        Scenario:
            1. Create an environment with "Neutron with tunneling
               segmentation" as a network configuration and CEPH storage
            2. Enable and configure Contrail plugin
            3. Deploy cluster with following node configuration:
                node-01: 'controller';
                node-02: 'controller';
                node-03: 'controller';
                node-04: 'compute', 'ceph-osd', 'dpdk';
                node-05: 'compute', 'ceph-osd';
                node-06: 'contrail-db';
                node-07: 'contrail-config';
                node-08: 'contrail-control';
            4. Run OSTF tests

        Duration 120 min

        """
        self.bm_drv.host_prepare(self)

        plugin.prepare_contrail_plugin(self, slaves=9,
                                       options={'images_ceph': True})

        # enable plugin in contrail settings
        plugin.activate_plugin(self)
        # activate DPDK feature
        plugin.activate_dpdk(self)
        # activate vSRX image
        vsrx_setup_result = plugin.activate_vsrx()

        self.bm_drv.setup_fuel_node(self,
                                    cluster_id=self.cluster_id,
                                    roles=['compute', 'ceph-osd', 'dpdk'])
        conf_nodes = {
            'slave-01': ['controller'],
            'slave-02': ['controller'],
            'slave-03': ['controller'],
            # 'slave-04': ['compute', 'ceph-osd', 'dpdk'],
            'slave-05': ['compute', 'ceph-osd'],
            'slave-06': ['contrail-db'],
            'slave-07': ['contrail-config'],
            'slave-08': ['contrail-control'],
        }
        openstack.update_deploy_check(self, conf_nodes,
                                      is_vsrx=True)

    @test(depends_on=[SetupEnvironment.prepare_slaves_9],
          groups=["contrail_dpdk_add_compute"])
    @log_snapshot_after_test
    @set_kvm_use
    def contrail_dpdk_add_compute(self):
        """Verify that Contrail compute role can be added after deploying

        Scenario:
            1. Create an environment with "Neutron with tunneling
               segmentation" as a network configuration
            2. Enable and configure Contrail plugin
            3. Deploy cluster with following node configuration:
                node-1: 'controller', 'ceph-osd';
                node-2: 'contrail-config', 'contrail-control', 'contrail-db';
                node-3: 'contrail-db';
                node-4: 'compute', 'ceph-osd', 'dpdk';
                node-5: 'compute', 'ceph-osd';
            4. Run OSTF tests
            5. Check Controller and Contrail nodes status
            6. Add one node with following configuration:
                node-6: "compute", "ceph-osd";
            7. Deploy changes
            8. Run OSTF tests

        """
        self.bm_drv.host_prepare(self)
        plugin.prepare_contrail_plugin(self, slaves=9,
                                       options={'images_ceph': True})

        # enable plugin in contrail settings
        plugin.activate_plugin(self)
        # activate DPDK feature
        plugin.activate_dpdk(self)
        # activate vSRX image
        vsrx_setup_result = plugin.activate_vsrx()

        self.bm_drv.setup_fuel_node(self,
                                    cluster_id=self.cluster_id,
                                    roles=['compute', 'ceph-osd', 'dpdk'])
        conf_nodes = {
            'slave-01': ['controller', 'ceph-osd'],
            'slave-02': ['contrail-config',
                         'contrail-control',
                         'contrail-db'],
            'slave-03': ['contrail-db'],
            # 'slave-04': ['compute', 'ceph-osd', 'dpdk'],
            'slave-05': ['compute', 'ceph-osd'],
            # Here we add slave-06
        }
        conf_compute = {'slave-06': ['compute', 'ceph-osd']}

        openstack.update_deploy_check(self, conf_nodes,
                                      is_vsrx=True)

        openstack.update_deploy_check(self, conf_compute,
                                      # FIXME: Disabled for DPDK
                                      is_vsrx=True)

    @test(depends_on=[SetupEnvironment.prepare_slaves_9],
          groups=["contrail_dpdk_delete_compute"])
    @log_snapshot_after_test
    @set_kvm_use
    def contrail_dpdk_delete_compute(self):
        """Verify that Contrail compute role can be deleted after deploying

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
        self.bm_drv.host_prepare(self)
        plugin.prepare_contrail_plugin(self, slaves=9)

        # enable plugin in contrail settings
        plugin.activate_plugin(self)
        # activate DPDK feature
        plugin.activate_dpdk(self)
        # activate vSRX image
        vsrx_setup_result = plugin.activate_vsrx()

        self.bm_drv.setup_fuel_node(self,
                                    cluster_id=self.cluster_id,
                                    roles=['compute', 'cinder', 'dpdk'])
        conf_no_compute = {
            'slave-01': ['controller'],
            'slave-02': ['contrail-control',
                         'contrail-config',
                         'contrail-db'],
            'slave-03': ['contrail-db'],
            # 'slave-04': ['compute', 'cinder', 'dpdk'],
            'slave-05': ['compute', 'cinder'],
            # Here slave-06
        }
        conf_compute = {'slave-06': ['compute']}

        openstack.update_deploy_check(self,
                                      dict(conf_no_compute, **conf_compute),
                                      is_vsrx=True)
        openstack.update_deploy_check(self,
                                      conf_compute, delete=True,
                                      is_vsrx=True)

    @test(depends_on=[SetupEnvironment.prepare_slaves_9],
          groups=["contrail_dpdk_add_dpdk"])
    @log_snapshot_after_test
    @set_kvm_use
    def contrail_dpdk_add_dpdk(self):
        """Verify that DPDK role can be added after deploying

        Scenario:
            1. Create an environment with "Neutron with tunneling
               segmentation" as a network configuration
            2. Enable and configure Contrail plugin
            3. Deploy cluster with following node configuration:
                node-01: 'controller';
                node-02: 'contrail-config', 'contrail-control', 'contrail-db';
                node-03: 'contrail-db';
                node-04: 'compute', 'ceph-osd', 'dpdk';
                node-05: 'compute', 'ceph-osd';
            4. Run OSTF tests
            6. Add one node with following configuration:
                node-6: "compute", "dpdk";
            7. Deploy changes
            8. Run OSTF tests

        """
        self.bm_drv.host_prepare(self)
        plugin.prepare_contrail_plugin(self, slaves=9,
                                       options={'images_ceph': True})

        # enable plugin in contrail settings
        plugin.activate_plugin(self)
        # activate DPDK feature
        plugin.activate_dpdk(self)
        # activate vSRX image
        vsrx_setup_result = plugin.activate_vsrx()

        self.bm_drv.setup_fuel_node(self,
                                    cluster_id=self.cluster_id,
                                    roles=['compute', 'ceph-osd', 'dpdk'])
        conf_nodes = {
            'slave-01': ['controller'],
            'slave-02': ['contrail-config',
                         'contrail-control',
                         'contrail-db'],
            'slave-03': ['contrail-db'],
            # 'slave-04': ['compute', 'ceph-osd', 'dpdk'],
            'slave-05': ['compute', 'ceph-osd'],
            # Here we add slave-06
        }
        conf_dpdk = {'slave-06': ['compute', 'dpdk']}

        openstack.update_deploy_check(self, conf_nodes,
                                      is_vsrx=True)

        openstack.update_deploy_check(self, conf_dpdk,
                                      is_vsrx=True)

    @test(depends_on=[SetupEnvironment.prepare_slaves_9],
          groups=["contrail_dpdk_delete_dpdk"])
    @log_snapshot_after_test
    @set_kvm_use
    def contrail_dpdk_delete_dpdk(self):
        """Verify that DPDK role can be deleted after deploying

        Scenario:
            1. Create an environment with "Neutron with tunneling
               segmentation" as a network configuration
            2. Enable and configure Contrail plugin
            3. Deploy cluster with following node configuration:
                node-01: 'controller', 'ceph-osd';
                node-02: 'contrail-control', 'contrail-config', 'contrail-db';
                node-03: 'contrail-db';
                node-04: 'compute', 'dpdk', 'ceph-osd';
                node-05: 'compute', 'dpdk';
                node-06: 'compute', 'ceph-osd';
            4. Run OSTF tests
            5. Delete node-05 with "dpdk" and "compute" roles
            6. Deploy changes
            7. Run OSTF tests

        """
        self.bm_drv.host_prepare(self)
        plugin.prepare_contrail_plugin(self, slaves=9,
                                       options={'images_ceph': True})

        # enable plugin in contrail settings
        plugin.activate_plugin(self)
        # activate DPDK feature
        plugin.activate_dpdk(self)
        # activate vSRX image
        vsrx_setup_result = plugin.activate_vsrx()

        self.bm_drv.setup_fuel_node(self,
                                    cluster_id=self.cluster_id,
                                    roles=['compute', 'ceph-osd', 'dpdk'])
        conf_no_dpdk = {
            'slave-01': ['controller', 'ceph-osd'],
            'slave-02': ['contrail-control',
                         'contrail-config',
                         'contrail-db'],
            'slave-03': ['contrail-db'],
            # 'slave-04': ['compute', 'ceph-osd', 'dpdk'],
            # Here slave-05
            'slave-06': ['compute', 'ceph-osd']
        }
        conf_dpdk = {'slave-05': ['compute', 'dpdk']}

        openstack.update_deploy_check(self,
                                      dict(conf_no_dpdk, **conf_dpdk),
                                      is_vsrx=True)
        openstack.update_deploy_check(self,
                                      conf_dpdk, delete=True,
                                      is_vsrx=True)
