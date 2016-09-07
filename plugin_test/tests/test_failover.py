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
import subprocess
import time
import libvirt

from proboscis import test
from proboscis.asserts import assert_true
from fuelweb_test import logger
from fuelweb_test.helpers.decorators import log_snapshot_after_test
from fuelweb_test.settings import CONTRAIL_PLUGIN_PACK_UB_PATH
from fuelweb_test.tests.base_test_case import SetupEnvironment
from fuelweb_test.tests.base_test_case import TestBasic
from helpers import vsrx
from helpers import plugin
from helpers import openstack
from helpers.settings import CONTRAIL_PLUGIN_VERSION
from tests.test_contrail_check import TestContrailCheck


@test(groups=["plugins"])
class FailoverTests(TestBasic):
    """FailoverTests."""

    pack_copy_path = '/var/www/nailgun/plugins/contrail-5.0'
    add_package = '/var/www/nailgun/plugins/contrail-5.0/'\
                  'repositories/ubuntu/contrail-setup*'
    ostf_msg = 'OSTF tests passed successfully.'
    cluster_id = ''
    pack_path = CONTRAIL_PLUGIN_PACK_UB_PATH
    CONTRAIL_DISTRIBUTION = os.environ.get('CONTRAIL_DISTRIBUTION')

    @test(depends_on=[SetupEnvironment.prepare_slaves_3],
          groups=["contrail_uninstall", "contrail_failover"])
    @log_snapshot_after_test
    def contrail_uninstall(self):
        """Check that plugin can be removed.

        Scenario:
            1. Install plugin and create cluster with activated plugin.
            2. Try to remove plugin and ensure that alert presents in cli:
               '400 Client Error: Bad Request (Can not delete plugin which
               is enabled for some environment.)'
            3. Remove environment.
            4. Remove plugin.
            5. Check that it was removed successfully.


        Duration: 5 min

        """
        # constants
        plugin_name = 'contrail'
        message = "400 Client Error: Bad Request for url: " + \
            "http://10.109.0.2:8000/api/v1/plugins/1 " + \
            "(Can't delete plugin which is enabled for some environment.)"

        self.show_step(1)
        plugin.prepare_contrail_plugin(self, slaves=3)
        plugin.activate_plugin(self)
        cluster_id = self.fuel_web.get_last_created_cluster()

        self.show_step(2)
        cmd = 'fuel plugins --remove {0}=={1}'.format(
            plugin_name, CONTRAIL_PLUGIN_VERSION)

        result = self.env.d_env.get_admin_remote().execute(cmd)
        assert_true(
            result['exit_code'] == 1,
            'Plugin is removed.')

        assert_true(
            result['stderr'].pop().splitlines().pop() == message,
            'Error message was not displayed.')

        self.show_step(3)
        self.fuel_web.delete_env_wait(cluster_id)

        self.show_step(4)
        result = self.env.d_env.get_admin_remote().execute(cmd)
        assert_true(
            result['exit_code'] == 0,
            'Plugin was not removed.')

        self.show_step(5)
        cmd = 'fuel plugins list'
        output = list(self.env.d_env.get_admin_remote().execute(
            cmd)['stdout']).pop().split(' ')

        assert_true(
            plugin_name not in output,
            "Plugin is not removed {}".format(plugin_name)
        )

    @test(depends_on=[SetupEnvironment.prepare_slaves_9],
          groups=["contrail_ha_with_node_problems", "contrail_failover"])
    @log_snapshot_after_test
    def contrail_ha_with_node_problems(self):
        """Check Contrail HA using node problems

        Scenario:
            1. Deploy openstack with HA (at lest 3 controllers and 3 nodes with contrail`s roles) and Ceph
            2. Run OSTF tests
            3. Run contrail health check tests
            4. Disable first contrail node via libvirt
            5. Run OSTF tests
            6. Run contrail health check tests
            7. Enable first contrail node, vait 5-10 minutes and disable second cotrail node
            8. Run OSTF test
            9. Run contrail health check tests
            10. Enable second contrail node, vait 5-10 minutes and disable third cotrail node
            11. Run OSTF tests
            12. Run contrail health check test
        """

        self.show_step(1)
        plugin.prepare_contrail_plugin(self, slaves=9,
                                       options={'images_ceph': True,
                                                'volumes_ceph': True,
                                                'ephemeral_ceph': True,
                                                'objects_ceph': True,
                                                'volumes_lvm': False})

        plugin.activate_plugin(self)
        # activate vSRX image
        vsrx_setup_result = vsrx.activate()


        conf_env = {
            'slave-01': ['controller'],
            'slave-02': ['controller'],
            'slave-03': ['controller'],
            'slave-04': ['compute', 'ceph-osd'],
            'slave-05': ['compute', 'ceph-osd'],
            'slave-06': ['compute', 'ceph-osd'],
            'slave-07': ['contrail-config',
                         'contrail-control',
                         'contrail-db',
                         'contrail-analytics'],
            'slave-08': ['contrail-config',
                         'contrail-control',
                         'contrail-db',
                         'contrail-analytics',],
            'slave-09': ['contrail-config',
                         'contrail-control',
                         'contrail-db',
                         'contrail-analytics'],
                    }

        self.show_step(2)
        openstack.update_deploy_check(self, conf_env,
                                      is_vsrx=vsrx_setup_result)

        self.show_step(3)
        TestContrailCheck(self).cloud_check(['contrail'])

        #open connection to qemu
        conn = libvirt.open('qemu:///system')
        if conn == None:
            raise ValueError("Failed to open connection to qemu:///system")
        else:
          logger.info("open connection to qemu:///system")
        #get list of domains
        node_list =conn.listAllDomains(0)

        i = 0
        while i < 3:
            m = 7
            n = str(m + i)
            for node in node_list:
                #find node with contrail
                if n in node.name():

                    self.show_step(4+i)
                    node.destroy() # stop node
                    logger.info("Node {0} was stopped".format(n))

                    self.show_step(5+i)
                    self.fuel_web.run_ostf(cluster_id=self.cluster_id,
                                           test_sets=['smoke', 'sanity', 'ha'])
                    self.show_step(6+i)
                    TestContrailCheck(self).cloud_check(['contrail'],
                                       ['test_contrail_node_status'])
                    node.create() # start node
                    logger.info("Node {0} was run".format(n))
                    break
            logger.info("Waiting for node {0}".format(n))
            time.sleep(6 * 60)
            i+=1
        conn.close()
