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
import time
import libvirt

from proboscis import test
from proboscis.asserts import assert_true
from proboscis.asserts import assert_equal
from fuelweb_test import logger
from fuelweb_test.helpers.decorators import log_snapshot_after_test
from fuelweb_test.settings import CONTRAIL_PLUGIN_PACK_UB_PATH
from fuelweb_test.tests import base_test_case
from helpers import vsrx
from helpers import plugin
from helpers import openstack
from helpers.settings import CONTRAIL_PLUGIN_VERSION
from helpers.settings import OSTF_RUN_TIMEOUT
from tests.test_contrail_check import TestContrailCheck


@test(groups=["plugins"])
class FailoverTests(base_test_case.TestBasic):
    """FailoverTests."""

    pack_copy_path = '/var/www/nailgun/plugins/contrail-5.1'
    add_package = '/var/www/nailgun/plugins/contrail-5.1/'\
                  'repositories/ubuntu/contrail-setup*'
    ostf_msg = 'OSTF tests passed successfully.'
    cluster_id = ''
    pack_path = CONTRAIL_PLUGIN_PACK_UB_PATH
    CONTRAIL_DISTRIBUTION = os.environ.get('CONTRAIL_DISTRIBUTION')

    @test(depends_on=[base_test_case.SetupEnvironment.prepare_slaves_3],
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

    @test(depends_on=[base_test_case.SetupEnvironment.prepare_slaves_9],
          groups=["contrail_ha_with_node_problems", "contrail_failover"])
    @log_snapshot_after_test
    def contrail_ha_with_node_problems(self):
        """Check Contrail HA using node problems

        Scenario:
            1. Deploy openstack with HA (at lest 3 controllers
               and 3 nodes with contrail`s roles) and Ceph
            2. Run OSTF tests
            3. Run contrail health check tests
            4. Disable first contrail node via libvirt
            5. Run OSTF tests
            6. Run contrail health check tests
            7. Enable first contrail node and wait 6 minutes
            8. Disable second cotrail node
            9. Run OSTF test
            10. Run contrail health check tests
            11. Enable second contrail node and wait 6 minutes
            12. Disable third cotrail node
            13. Run OSTF tests
            14. Run contrail health check test
            15. Enable third node
            16. Run OSTF tests
            17. Run contrail health check test
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
            'slave-01': ['controller', 'ceph-osd'],
            'slave-02': ['controller', 'ceph-osd'],
            'slave-03': ['controller', 'ceph-osd'],
            'slave-04': ['contrail-controller'],
            'slave-05': ['contrail-controller'],
            'slave-06': ['contrail-controller'],
            'slave-07': ['contrail-analytics', 'contrail-analytics-db'],
            'slave-08': ['contrail-analytics', 'contrail-analytics-db'],
            'slave-09': ['contrail-analytics', 'contrail-analytics-db'],
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

        for i in range(0,3):
            m = 7
            n = str(m + i)
            steps  = [4, 5, 6, 7]

            for index, step in enumerate(steps):
                steps[index] = step + (4 * i)

            for node in node_list:
                #find node with contrail
                if n in node.name():

                    self.show_step(steps[0])
                    node.destroy() # stop node
                    logger.info("Node {0} was stopped".format(n))

                    self.show_step(steps[1])
                    self.fuel_web.run_ostf(cluster_id=self.cluster_id,
                                           test_sets=['smoke', 'sanity', 'ha'])
                    self.show_step(steps[2])
                    TestContrailCheck(self).cloud_check(['contrail'],
                                       ['test_contrail_node_status'])

                    self.show_step(steps[3])
                    node.create() # start node
                    logger.info("Node {0} was run".format(n))
                    break
            logger.info("Waiting for node {0}".format(n))
            time.sleep(6 * 60)
        conn.close()

        self.show_step(16)
        if vsrx_setup_result:
            self.fuel_web.run_ostf(cluster_id=self.cluster_id,
                                   test_sets=['smoke', 'sanity', 'ha'],
                                   timeout=OSTF_RUN_TIMEOUT)

        self.show_step(17)
        TestContrailCheck(self).cloud_check(['contrail'])


    @test(depends_on=[SetupEnvironment.prepare_slaves_9],
          groups=["contrail_ha_with_network_problems", "contrail_failover"])
    @log_snapshot_after_test
    def contrail_ha_with_network_problems(self):
        """Check Contrail HA using network problems

        Scenario:
            1. Deploy openstack with HA (at lest 3 controllers
               and 3 nodes with contrail`s roles)
            2. Run OSTF tests
            3. Run contrail health check tests
            4. Connect to a contrail controller host, stop the network
               interfaces connected to private and management networks
            5. Run OSTF tests
            6. Run contrail health check tests
        """

        self.show_step(1)
        plugin.prepare_contrail_plugin(self, slaves=9)

        plugin.activate_plugin(self)
        # activate vSRX image
        vsrx_setup_result = vsrx.activate()

        conf_env = {
            'slave-01': ['controller'],
            'slave-02': ['controller'],
            'slave-03': ['controller'],
            'slave-04': ['contrail-controller'],
            'slave-05': ['contrail-controller'],
            'slave-06': ['contrail-controller'],
            'slave-07': ['contrail-analytics', 'contrail-analytics-db'],
            'slave-08': ['contrail-analytics', 'contrail-analytics-db'],
            'slave-09': ['contrail-analytics', 'contrail-analytics-db'],
        }

        self.show_step(2)
        openstack.update_deploy_check(self, conf_env,
                                      is_vsrx=vsrx_setup_result)

        self.show_step(3)
        TestContrailCheck(self).cloud_check(['contrail'])

        self.show_step(4)

        def get_interface_name4role(cluster_id, node_name, role):
            logger.info('[get_interface_name4role] cluster_id: {0}, '
                        'node: {1}, '
                        'role:{2}'.format(cluster_id, node_name, role))
            nailgun_node = None
            for node in self.fuel_web.client.list_cluster_nodes(cluster_id):
                logger.info('Check node {0} for name: {1}'.format(node['name'],
                                                                  node_name))
                if node_name in node['name']:
                    nailgun_node = node
                    break
            else:
                assert 'slave-01 node not found in cluster: {0}'.format(
                    self.cluster_id)

            interfaces = self.fuel_web.client.get_node_interfaces(
                nailgun_node['id'])
            for iface in interfaces:
                for net in iface['assigned_networks']:
                    logger.info('Check iface {0} for role {1}'.format(
                        iface['name'], role))
                    if role in net['name']: # check role name for interface
                        logger.info('Found interface: {0}'.format(
                            iface['name']))
                        return iface['name'] # return interface name
            return ''

        cluster_id = self.cluster_id
        ifaces = [
            get_interface_name4role(cluster_id, 'slave-01', 'private'),
            get_interface_name4role(cluster_id, 'slave-01', 'management')
        ]
        for iface in ifaces:
            cmd = 'sudo ifconfig {0} down'.format(iface)
            with self.fuel_web.get_ssh_for_node("slave-01") as remote:
                res_pgrep = remote.execute(cmd)
                assert_equal(0, res_pgrep['exit_code'],
                             'Failed with error code:{0}, {1}, out:{2}'.format(
                                 res_pgrep['exit_code'],
                                 res_pgrep['stderr'],
                                 res_pgrep['stdout']))
        self.show_step(5)
        if vsrx_setup_result:
            self.fuel_web.run_ostf(cluster_id=self.cluster_id,
                                   test_sets=['smoke', 'sanity', 'ha'],
                                   timeout=OSTF_RUN_TIMEOUT)
        self.show_step(6)
        TestContrailCheck(self).cloud_check(['contrail'])
