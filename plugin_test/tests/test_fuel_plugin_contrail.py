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
from copy import deepcopy

from proboscis import test
from proboscis.asserts import assert_true

from fuelweb_test.helpers.decorators import log_snapshot_after_test
from fuelweb_test.helpers import checkers
from fuelweb_test.helpers.common import Common
from fuelweb_test import logger
from fuelweb_test.settings import DEPLOYMENT_MODE
from fuelweb_test.settings import CONTRAIL_PLUGIN_PATH
from fuelweb_test.settings import CONTRAIL_PLUGIN_PACK_UB_PATH
from fuelweb_test.settings import CONTRAIL_PLUGIN_PACK_CEN_PATH
from fuelweb_test.tests.base_test_case import SetupEnvironment
from fuelweb_test.tests.base_test_case import TestBasic
from fuelweb_test.helpers.checkers import check_repo_managment

BOND_CONFIG = [{
    'mac': None,
    'mode': 'active-backup',
    'name': 'lnx-bond0',
    'slaves': [
        {'name': 'eth4'},
        {'name': 'eth2'}
    ],
    'state': None,
    'type': 'bond',
    'assigned_networks': []}]

INTERFACES = {
    'eth0': ['fuelweb_admin'],
    'eth1': ['public'],
    'eth3': ['private'],
    'lnx-bond0': ['management',
                  'storage',
                  ]
}


@test(groups=["plugins"])
class ContrailPlugin(TestBasic):
    """ContrailPlugin."""  # TODO documentation

    pack_copy_path = '/var/www/nailgun/plugins/contrail-2.0'
    add_ub_packag = \
        '/var/www/nailgun/plugins/contrail-2.0/' \
        'repositories/ubuntu/contrail-setup*'
    add_cen_packeg = \
        '/var/www/nailgun/plugins/contrail-2.0/' \
        'repositories/centos/Packages/contrail-setup*'
    ostf_msg = 'OSTF tests passed successfully.'

    cluster_id = ''

    pack_path = [CONTRAIL_PLUGIN_PACK_UB_PATH, CONTRAIL_PLUGIN_PACK_CEN_PATH]

    NEUTRON_BOND_CONFIG = deepcopy(BOND_CONFIG)
    NEUTRON_INTERFACES = deepcopy(INTERFACES)
    CONTRAIL_DISTRIBUTION = os.environ.get('CONTRAIL_DISTRIBUTION')

    def upload_contrail_packages(self):
        for pack in self.pack_path:
            node_ssh = self.env.d_env.get_admin_remote()
            if os.path.splitext(pack)[1] in [".deb", ".rpm"]:
                pkg_name = os.path.basename(pack)
                logger.debug("Uploading package {0} "
                             "to master node".format(pkg_name))
                node_ssh.upload(pack, self.pack_copy_path)
            else:
                logger.error('Failed to upload file')

    def install_packages(self, remote):
        command = "cd " + self.pack_copy_path + " && ./install.sh"
        logger.info('The command is %s', command)
        remote.execute_async(command)
        time.sleep(50)
        os.path.isfile(self.add_ub_packag or self.add_cen_packeg)

    def assign_net_provider(self, pub_all_nodes=False, ceph_value=False):
        """Assign neutron with gre segmentation"""
        segment_type = 'gre'
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
            self.env.d_env.get_admin_remote(),
            CONTRAIL_PLUGIN_PATH, '/var')

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
            self.fuel_web.check_plugin_exists(self.cluster_id, plugin_name),
            msg)
        logger.debug('we have contrail element')
        if self.CONTRAIL_DISTRIBUTION == 'juniper':
            option = {'metadata/enabled': True,
                      'contrail_distribution/value': 'juniper', }
        else:
            option = {'metadata/enabled': True, }
        self.fuel_web.update_plugin_data(self.cluster_id, plugin_name, option)

    def create_net_subnet(self, cluster):
        """Create net and subnet"""
        contrail_ip = self.fuel_web.get_public_vip(cluster)
        logger.info('The ip is %s', contrail_ip)
        net = Common(
            controller_ip=contrail_ip, user='admin',
            password='admin', tenant='admin'
        )

        net.neutron.create_network(body={
            'network': {
                'name': 'net04',
                'admin_state_up': True,
            }
        })

        network_id = ''
        network_dic = net.neutron.list_networks()
        for dd in network_dic['networks']:
            if dd.get("name") == "net04":
                network_id = dd.get("id")

        if network_id == "":
            logger.error('Network id empty')

        logger.debug("id {0} to master node".format(network_id))

        net.neutron.create_subnet(body={
            'subnet': {
                'network_id': network_id,
                'ip_version': 4,
                'cidr': '10.100.0.0/24',
                'name': 'subnet04',
            }
        })

    def change_disk_size(self):
        """
        Configure disks on base-os nodes
        """
        nailgun_nodes = \
            self.fuel_web.client.list_cluster_nodes(self.cluster_id)
        base_os_disk = 332236
        base_os_disk_gb = ("{0}G".format(round(base_os_disk / 1024, 1)))
        logger.info('disk size is {0}'.format(base_os_disk_gb))
        disk_part = {
            "vda": {
                "os": base_os_disk, }
        }

        for node in nailgun_nodes:
            if node.get('pending_roles') == ['base-os']:
                self.fuel_web.update_node_disk(node.get('id'), disk_part)

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

    @test(depends_on=[SetupEnvironment.prepare_slaves_5],
          groups=["install_contrail"])
    @log_snapshot_after_test
    def install_contrail(self):
        """Install Contrail Plugin and create cluster

        Scenario:
            1. Revert snapshot "ready_with_5_slaves"
            2. Upload contrail plugin to the master node
            3. Install plugin and additional packages
            4. Enable Neutron with VLAN segmentation
            5. Create cluster

        Duration 20 min

        """
        self.prepare_contrail_plugin(slaves=5)

