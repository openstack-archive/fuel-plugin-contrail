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
import time
from proboscis import test
from proboscis.asserts import assert_true
from fuelweb_test.helpers import checkers
from fuelweb_test import logger
from fuelweb_test.settings import DEPLOYMENT_MODE
from fuelweb_test.settings import CONTRAIL_PLUGIN_PATH
from fuelweb_test.settings import CONTRAIL_PLUGIN_PACK_UB_PATH
from fuelweb_test.helpers.checkers import check_repo_managment


@test(groups=["plugins"])
class PluginActions(object):
    """Methods for plugin actions"""

    # variables
    pack_copy_path = '/var/www/nailgun/plugins/contrail-3.0'
    add_package = '/var/www/nailgun/plugins/contrail-3.0/' \
        'repositories/ubuntu/contrail-setup*'
    ostf_msg = 'OSTF tests passed successfully.'

    cluster_id = ''

    pack_path = CONTRAIL_PLUGIN_PACK_UB_PATH

    CONTRAIL_DISTRIBUTION = os.environ.get('CONTRAIL_DISTRIBUTION')

    def upload_contrail_packages(self):
        node_ssh = self.env.d_env.get_admin_remote()
        if os.path.splitext(self.pack_path)[1] == ".deb":
            pkg_name = os.path.basename(self.pack_path)
            logger.debug("Uploading package {0} to master node".format(pkg_name))
            node_ssh.upload(self.pack_path, self.pack_copy_path)
        else:
            raise Exception('Failed to upload file to the master node')

    def install_packages(self, remote):
        command = "cd " + self.pack_copy_path + " && ./install.sh"
        logger.info('The command is %s', command)
        remote.execute_async(command)
        time.sleep(50)
        os.path.isfile(self.add_package)

    def assign_net_provider(self, pub_all_nodes=False, ceph_value=False):
        """Assign neutron with tunneling segmentation"""
        segment_type = 'tun'
        self.cluster_id = self.fuel_web.create_cluster(
            name=self.__class__.__name__,
            mode=DEPLOYMENT_MODE,
            settings={
                "net_provider": 'neutron',
                "net_segment_type": segment_type,
                "assign_to_all_nodes": pub_all_nodes,
                "images_ceph": ceph_value
            }
        )
        return self.cluster_id

    def prepare_contrail_plugin(
            self, slaves=None, pub_all_nodes=False, ceph_value=False):
        """Copy necessary packages to the master node and install them"""

        self.env.revert_snapshot("ready_with_%d_slaves" % slaves)

        # copy plugin to the master node
        checkers.upload_tarball(
            self.env.d_env.get_admin_remote(), CONTRAIL_PLUGIN_PATH, '/var')

        # install plugin
        checkers.install_plugin_check_code(
            self.env.d_env.get_admin_remote(),
            plugin=os.path.basename(CONTRAIL_PLUGIN_PATH))

        if self.CONTRAIL_DISTRIBUTION == 'juniper':
            # copy additional packages to the master node
            self.upload_contrail_packages()

            # install packages
            self.install_packages(self.env.d_env.get_admin_remote())

        # prepare fuel
        self.assign_net_provider(pub_all_nodes, ceph_value)

    def activate_plugin(self):
        """Enable plugin in contrail settings"""
        plugin_name = 'contrail'
        msg = "Plugin couldn't be enabled. Check plugin version. Test aborted"
        assert_true(
            self.fuel_web.check_plugin_exists(self.cluster_id, plugin_name), msg)
        logger.debug('we have contrail element')
        if self.CONTRAIL_DISTRIBUTION == 'juniper':
            option = {'metadata/enabled': True,
                      'contrail_distribution/value': 'juniper', }
        else:
            option = {'metadata/enabled': True, }
        self.fuel_web.update_plugin_data(self.cluster_id, plugin_name, option)

    def deploy_cluster(self):
        """
        Deploy cluster with additional time for waiting on node's availability
        """
        try:
            self.fuel_web.deploy_cluster_wait(
                self.cluster_id, check_services=False)
        except:
            nailgun_nodes = self.env.fuel_web.client.list_cluster_nodes(
                self.env.fuel_web.get_last_created_cluster())
            time.sleep(420)
            for n in nailgun_nodes:
                check_repo_managment(
                    self.env.d_env.get_ssh_to_remote(n['ip']))
                logger.info('ip is {0}'.format(n['ip'], n['name']))
