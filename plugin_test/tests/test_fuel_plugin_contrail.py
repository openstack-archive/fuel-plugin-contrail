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
import re
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

    pack_copy_path = '/var/www/nailgun/plugins/contrail-2.1'
    add_package = \
        '/var/www/nailgun/plugins/contrail-2.1/' \
        'repositories/ubuntu/contrail-setup*'
    ostf_msg = 'OSTF tests passed successfully.'

    cluster_id = ''

    pack_path = CONTRAIL_PLUGIN_PACK_UB_PATH

    NEUTRON_BOND_CONFIG = deepcopy(BOND_CONFIG)
    NEUTRON_INTERFACES = deepcopy(INTERFACES)
    CONTRAIL_DISTRIBUTION = os.environ.get('CONTRAIL_DISTRIBUTION')

    def upload_contrail_packages(self):
        node_ssh = self.env.d_env.get_admin_remote()
        if os.path.splitext(self.pack_path)[1] == ".deb":
                pkg_name = os.path.basename(self.pack_path)
                logger.debug("Uploading package {0} "
                             "to master node".format(pkg_name))
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

    def node_rename(self, node_name_regexp, new_name, update_all=False):
        """Update nodes with new name
        """
        re_obj = re.compile(node_name_regexp)
        configured_nodes = self.fuel_web.client.list_nodes()

        nodes4update = []
        for node in configured_nodes:
            node_data = {
                'cluster_id': node['cluster'],
                'id': node['id'],
                'pending_addition': node['pending_addition'],
                'pending_deletion': node['pending_deletion'],
                'pending_roles': node['pending_roles'],
            }
            if re_obj.match(node['name']):
                logger.info("Rename node '%s' to '%s'" % (node['name'], new_name))
                node_data['name'] = new_name
                nodes4update.append(node_data)
            else:
                if update_all:
                    node_data['name'] = node['name']
                    nodes4update.append(node_data)

        return self.fuel_web.client.update_nodes(nodes4update)


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

    @test(depends_on=[SetupEnvironment.prepare_slaves_5],
          groups=["deploy_contrail"])
    @log_snapshot_after_test
    def deploy_contrail(self):
        """Deploy a cluster with Contrail Plugin

        Scenario:
            1. Revert snapshot "ready_with_5_slaves"
            2. Create cluster
            3. Add 3 nodes with Operating system role
               and 1 node with controller role
            4. Enable Contrail plugin
            5. Deploy cluster with plugin

        Duration 90 min

        """
        self.prepare_contrail_plugin(slaves=5)

        self.fuel_web.update_nodes(
            self.cluster_id,
            {
                'slave-01': ['base-os'],
                'slave-02': ['base-os'],
                'slave-03': ['base-os'],
                'slave-04': ['controller'],
            },
            contrail=True
        )

        # configure disks on base-os nodes
        self.change_disk_size()

        # enable plugin in contrail settings
        self.activate_plugin()

        # deploy cluster
        self.deploy_cluster()

    @test(depends_on=[SetupEnvironment.prepare_slaves_5],
          groups=["deploy_contrail_plugin_with_the_same_names"])
    @log_snapshot_after_test
    def deploy_contrail_plugin_with_the_same_names(self):
        """Verify deploy correctness with the same Contrail Controllers names

        Open the Settings tab of the Fuel web UI
        Select the Contrail plugin checkbox and configure plugin settings
        Configure network
        Add 3 nodes with "Operating system" role
        Rename one node in the template "contrail-1" and other two "contrail-2"
        Add 1 node with "Controller" role and 1 node with "Compute" role and start deploy.
        Check Controller, Compute and Contrail nodes status and start deploy.
        After the end of deploy run OSTF tests

        Expected Result
        All steps must be completed successfully, without any errors.
        """

        self.prepare_contrail_plugin(slaves=5)

        self.fuel_web.update_nodes(
            self.cluster_id,
            {
                'slave-01': ['base-os'],
                'slave-02': ['base-os'],
                'slave-03': ['base-os'],
                'slave-04': ['controller'],
                'slave-05': ['compute'],
            },
            contrail=True
        )

        self.node_rename('contrail-[2,3]', new_name='contrail-2', update_all=False)

        # configure disks on base-os nodes
        self.change_disk_size()

        # enable plugin in contrail settings
        self.activate_plugin()

        # deploy cluster
        self.deploy_cluster()

        # create net and subnet
        self.create_net_subnet(self.cluster_id)

        # run OSTF

        # TODO
        # Tests using north-south connectivity are expected to fail because
        # they require additional gateway nodes, and specific contrail
        # settings. This mark is a workaround until it's verified
        # and tested manually.
        # When it will be done 'should_fail=2' and
        # 'failed_test_name' parameter should be removed.

        self.fuel_web.run_ostf(cluster_id=self.cluster_id,
                               should_fail=2,
                               failed_test_name=[
                                   'Check network connectivity '
                                   'from instance via floating IP',
                                   'Launch instance with file injection'])


    @test(depends_on=[SetupEnvironment.prepare_slaves_5],
          groups=["contrail_bvt"])
    @log_snapshot_after_test
    def contrail_bvt(self):
        """BVT test for contrail plugin
        Deploy cluster with 1 controller, 1 compute,
        3 base-os and install contrail plugin

        Scenario:
            1. Revert snapshot "ready_with_5_slaves"
            2. Create cluster
            3. Add 3 nodes with Operating system role, 1 node with controller
               role and 1 node with compute + cinder role
            4. Enable Contrail plugin
            5. Deploy cluster with plugin
            6. Create net and subnet
            7. Run OSTF tests

        Duration 110 min

        """
        self.prepare_contrail_plugin(slaves=5)

        self.fuel_web.update_nodes(
            self.cluster_id,
            {
                'slave-01': ['base-os'],
                'slave-02': ['base-os'],
                'slave-03': ['base-os'],
                'slave-04': ['controller'],
                'slave-05': ['compute', 'cinder'],
            },
            contrail=True
        )

        # configure disks on base-os nodes
        self.change_disk_size()

        # enable plugin in contrail settings
        self.activate_plugin()

        # deploy cluster
        self.deploy_cluster()

        # create net and subnet
        self.create_net_subnet(self.cluster_id)

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

    @test(depends_on=[SetupEnvironment.prepare_slaves_3],
          groups=["contrail_spec_pass"])
    @log_snapshot_after_test
    def contrail_spec_pass(self):
        """Deploy cluster with 1 controller, 1 compute,
        3 base-os and install contrail plugin

        Scenario:
            1. Revert snapshot "ready_with_3_slaves"
            2. Create cluster
            3. Add a node with Operating system role, a node with controller
               role and a node with compute + cinder role
            4. Enable Contrail plugin
            5. Change password for administrator in settings tab using special characters
            6. Deploy cluster with plugin
            7. Create net and subnet
            8. Run OSTF tests

        Duration 110 min
        """
        self.prepare_contrail_plugin(slaves=3)

        def cluster_update_settings(cluster_id, settings={}):
            logger.info("Update cluster settings to %s", settings)
            attributes = self.fuel_web.client.get_cluster_attributes(cluster_id)

            for option in settings:
                section = False
                if option in ('sahara', 'murano', 'ceilometer', 'mongo'):
                    section = 'additional_components'
                if option in ('mongo_db_name', 'mongo_replset', 'mongo_user',
                              'hosts_ip', 'mongo_password'):
                    section = 'external_mongo'
                if option in ('volumes_ceph', 'images_ceph', 'ephemeral_ceph',
                              'objects_ceph', 'osd_pool_size', 'volumes_lvm',
                              'volumes_vmdk', 'images_vcenter'):
                    section = 'storage'
                if option in ('tenant', 'password', 'user'):
                    section = 'access'
                if option == 'assign_to_all_nodes':
                    section = 'public_network_assignment'
                if option in ('dns_list'):
                    section = 'external_dns'
                if option in ('ntp_list'):
                    section = 'external_ntp'
                if section:
                    attributes['editable'][section][option]['value'] =\
                        settings[option]

            logger.debug("Try to update cluster "
             "with next attributes {0}".format(attributes))
            res = self.fuel_web.client.update_cluster_attributes(cluster_id, attributes)
            return res

        cluster_settings = {
            'user': 'admin',
            'password': 'pass\/\/@$"\'&'
        }
        res = cluster_update_settings(self.cluster_id, cluster_settings)

        self.fuel_web.update_nodes(
            self.cluster_id,
            {
                'slave-01': ['base-os'],
                'slave-02': ['controller'],
                'slave-03': ['compute', 'cinder'],
            },
            contrail=True
        )

        # configure disks on base-os nodes
        self.change_disk_size()

        # enable plugin in contrail settings
        self.activate_plugin()

        # deploy cluster
        self.deploy_cluster()

        # create net and subnet
        self.create_net_subnet(self.cluster_id)

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
          groups=["contrail_plugin_add_delete_compute_node"])
    @log_snapshot_after_test
    def contrail_plugin_add_delete_compute_node(self):
        """Verify that Compute node can be
        deleted and added after deploying

        Scenario:
            1. Revert snapshot "ready_with_9_slaves"
            2. Create cluster
            3. Add 3 nodes with Operating system role,
               1 node with controller role and 2 nodes with compute role
            4. Enable Contrail plugin
            5. Deploy cluster with plugin
            6. Remove 1 node with compute role.
            7. Deploy cluster
            8. Add 1 nodes with compute role
            9. Deploy cluster
            10. Run OSTF tests

        Duration 140 min

        """
        self.prepare_contrail_plugin(slaves=9)

        # create cluster: 3 nodes with Operating system role,
        # 1 node with controller role and 2 nodes with compute role
        self.fuel_web.update_nodes(
            self.cluster_id,
            {
                'slave-01': ['base-os'],
                'slave-02': ['base-os'],
                'slave-03': ['base-os'],
                'slave-04': ['controller'],
                'slave-05': ['compute'],
                'slave-06': ['compute'],
            },
            contrail=True
        )

        # configure disks on base-os nodes
        self.change_disk_size()

        # enable plugin in contrail settings
        self.activate_plugin()

        # deploy cluster
        self.deploy_cluster()

        # create net and subnet
        self.create_net_subnet(self.cluster_id)

        #  remove one node with compute role
        self.fuel_web.update_nodes(
            self.cluster_id, {'slave-05': ['compute']}, False, True)

        self.deploy_cluster()

        # add 1 node with compute role and redeploy cluster
        self.fuel_web.update_nodes(
            self.cluster_id, {'slave-07': ['compute'], })

        self.deploy_cluster()

        # TODO
        # Tests using north-south connectivity are expected to fail because
        # they require additional gateway nodes, and specific contrail
        # settings. This mark is a workaround until it's verified
        # and tested manually.
        # Also workaround according to bug 1457515
        # When it will be done 'should_fail=3' and
        # 'failed_test_name' parameter should be removed.

        self.fuel_web.run_ostf(
            cluster_id=self.cluster_id,
            should_fail=3,
            failed_test_name=[('Check network connectivity '
                               'from instance via floating IP'),
                              ('Launch instance with file injection'),
                              ('Check that required services are running')]
        )

    @test(depends_on=[SetupEnvironment.prepare_slaves_9],
          groups=["deploy_ha_contrail_plugin"])
    @log_snapshot_after_test
    def deploy_ha_contrail_plugin(self):
        """Deploy HA Environment with Contrail Plugin

        Scenario:
            1. Revert snapshot "ready_with_9_slaves"
            2. Create cluster
            3. Add 3 nodes with Operating system role and
               1 node with controller role
            4. Enable Contrail plugin
            5. Deploy cluster with plugin
            6. Add 1 node with compute role
            7. Deploy cluster
            8. Run OSTF tests
            9. Add 2 nodes with controller role and
               1 node with compute + cinder role
            10. Deploy cluster
            11. Run OSTF tests

        Duration 140 min

        """
        self.prepare_contrail_plugin(slaves=9)

        # create cluster: 3 nodes with Operating system role
        # and 1 node with controller role
        self.fuel_web.update_nodes(
            self.cluster_id,
            {
                'slave-01': ['base-os'],
                'slave-02': ['base-os'],
                'slave-03': ['base-os'],
                'slave-04': ['controller'],
            },
            contrail=True
        )

        # configure disks on base-os nodes
        self.change_disk_size()

        # enable plugin in contrail settings
        self.activate_plugin()

        self.deploy_cluster()

        # create net and subnet
        self.create_net_subnet(self.cluster_id)

        #  add 1 node with compute role and redeploy cluster
        self.fuel_web.update_nodes(
            self.cluster_id, {'slave-05': ['compute']},)

        self.deploy_cluster()

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

        # add to cluster 2 nodes with controller role and one
        # with compute, cinder role and deploy cluster
        self.fuel_web.update_nodes(
            self.cluster_id,
            {
                'slave-06': ['controller'],
                'slave-07': ['controller'],
                'slave-08': ['compute', 'cinder'],
            }
        )

        logger.info(self.ostf_msg)

        self.deploy_cluster()

        #TODO
        # Tests using north-south connectivity are expected to fail because
        # they require additional gateway nodes, and specific contrail
        # settings. This mark is a workaround until it's verified
        # and tested manually.
        # When it will be done 'should_fail=2' and
        # 'failed_test_name' parameter should be removed.

        self.fuel_web.run_ostf(
            cluster_id=self.cluster_id,
            test_sets=['smoke', 'sanity', 'ha'],
            should_fail=2,
            failed_test_name=[('Check network connectivity '
                               'from instance via floating IP'),
                              ('Launch instance with file injection')]
        )

    @test(depends_on=[SetupEnvironment.prepare_slaves_9],
          groups=["contrail_plugin_add_delete_controller_node"])
    @log_snapshot_after_test
    def contrail_plugin_add_delete_controller_node(self):
        """Verify that Controller node can be
        deleted and added after deploying

        Scenario:
            1. Revert snapshot "ready_with_9_slaves"
            2. Create cluster
            3. Add 3 nodes with Operating system role,
               2 nodes with controller role and 1 node with compute role
            4. Enable Contrail plugin
            5. Deploy cluster with plugin
            6. Remove 1 node with controller role.
            7. Deploy cluster
            8. Add 1 nodes with controller role
            9. Deploy cluster
            10. Run OSTF tests

        Duration 140 min

        """
        self.prepare_contrail_plugin(slaves=9)

        # create cluster: 3 nodes with Operating system role
        # and 1 node with controller role
        self.fuel_web.update_nodes(
            self.cluster_id,
            {
                'slave-01': ['base-os'],
                'slave-02': ['base-os'],
                'slave-03': ['base-os'],
                'slave-04': ['controller'],
                'slave-05': ['controller'],
                'slave-06': ['controller'],
                'slave-07': ['compute']
            },
            contrail=True
        )

        # configure disks on base-os nodes
        self.change_disk_size()

        # enable plugin in contrail settings
        self.activate_plugin()

        self.deploy_cluster()

        #  remove one node with controller role
        self.fuel_web.update_nodes(
            self.cluster_id, {'slave-05': ['controller']}, False, True)

        self.deploy_cluster()

        # add 1 node with controller role and redeploy cluster
        self.fuel_web.update_nodes(
            self.cluster_id, {'slave-08': ['controller']})

        self.deploy_cluster()

        # TODO
        # Tests using north-south connectivity are expected to fail because
        # they require additional gateway nodes, and specific contrail
        # settings. This mark is a workaround until it's verified
        # and tested manually.
        # Also workaround according to bug 1457515
        # When it will be done 'should_fail=3' and
        # 'failed_test_name' parameter should be removed.

        # create net and subnet to pass ostf
        self.create_net_subnet(self.cluster_id)

        self.fuel_web.run_ostf(
            cluster_id=self.cluster_id,
            should_fail=3,
            failed_test_name=[('Check network connectivity '
                               'from instance via floating IP'),
                              ('Launch instance with file injection'),
                              ('Check that required services are running')]
        )

    @test(depends_on=[SetupEnvironment.prepare_slaves_9],
          groups=["deploy_ha_with_pub_net_all_nodes"])
    @log_snapshot_after_test
    def deploy_ha_with_pub_net_all_nodes(self):
        """Deploy HA Environment with Contrail Plugin
        and assign public network to all nodes

        Scenario:
            1. Revert snapshot "ready_with_9_slaves"
            2. Create cluster and select "Assign public network to all nodes"
               check box
            3. Add 3 nodes with Operating system role,
               1 node with controller role and 1 node with compute role
            4. Enable Contrail plugin
            5. Deploy cluster with plugin
            6. Add 1 node with controller node and
               1 node with compute role
            7. Deploy cluster
            8. Run OSTF tests

        Duration 140 min

        """
        self.prepare_contrail_plugin(slaves=9, pub_all_nodes=True)

        # create cluster: 3 nodes with Operating system role,
        # 1 node with controller and 1 node with compute roles
        self.fuel_web.update_nodes(
            self.cluster_id,
            {
                'slave-01': ['base-os'],
                'slave-02': ['base-os'],
                'slave-03': ['base-os'],
                'slave-04': ['controller'],
                'slave-05': ['compute'],
            },
            contrail=True
        )

        # configure disks on base-os nodes
        self.change_disk_size()

        # enable plugin in contrail settings
        self.activate_plugin()

        self.deploy_cluster()

        # create net and subnet
        self.create_net_subnet(self.cluster_id)

        #  add 1 node with controller and 1 node with
        # compute role and redeploy cluster
        self.fuel_web.update_nodes(
            self.cluster_id, {
                'slave-06': ['compute'],
                'slave-07': ['compute', 'cinder']})

        self.deploy_cluster()

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
                              ('Launch instance with file injection')])

    @test(depends_on=[SetupEnvironment.prepare_slaves_5],
          groups=["check_bonding_with_contrail"])
    @log_snapshot_after_test
    def check_bonding_with_contrail(self):
        """Verify bonding with Contrail Plugin

        Scenario:
            1. Revert snapshot "ready_with_5_slaves"
            2. Create cluster
            3. Add 3 nodes with Operating system role,
               1 node with controller role and 1 node with compute role
            4. Enable Contrail plugin
            5. Setup bonding for management and storage interfaces
            6. Deploy cluster with plugin
            7. Run OSTF tests

        Duration 140 min

        """
        self.prepare_contrail_plugin(slaves=5)

        # create cluster: 3 nodes with Operating system role,
        # 1 node with controller and 1 node with compute roles
        self.fuel_web.update_nodes(
            self.cluster_id,
            {
                'slave-01': ['base-os'],
                'slave-02': ['base-os'],
                'slave-03': ['base-os'],
                'slave-04': ['controller'],
                'slave-05': ['compute'],
            },
            contrail=True
        )

        cluster_nodes = \
            self.fuel_web.client.list_cluster_nodes(self.cluster_id)
        for node in cluster_nodes:
            self.fuel_web.update_node_networks(
                node['id'], interfaces_dict=self.NEUTRON_INTERFACES,
                raw_data=self.NEUTRON_BOND_CONFIG
            )

        # enable plugin in contrail settings
        self.activate_plugin()

        self.deploy_cluster()

        # create net and subnet
        self.create_net_subnet(self.cluster_id)

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

    @test(depends_on=[SetupEnvironment.prepare_slaves_5],
          groups=["contrail_plugin_add_contrail_controller_node"])
    @log_snapshot_after_test
    def contrail_plugin_add_contrail_controller_node(self):
        """Verify Contrail Controller node can be added after deploying

        Scenario:
            1. Revert snapshot "ready_with_5_slaves"
            2. Create cluster
            3. Add 1 node with Operating system role,
                1 node with controller role and 1 node with compute role
            4. Enable Contrail plugin
            5. Deploy cluster with plugin
            6. Add 2 nodes with Operating system role
            7. Deploy cluster
            8. Run OSTF tests

        Duration 140 min
        :return:
        """
        self.prepare_contrail_plugin(slaves=5)

        # create cluster: 1 node with Operating system role,
        # 1 node with controller and 1 node with compute roles
        self.fuel_web.update_nodes(
            self.cluster_id,
            {
                'slave-01': ['base-os'],
                'slave-02': ['controller'],
                'slave-03': ['compute'],
                },
            contrail=True
        )

        # configure disks on base-os nodes
        self.change_disk_size()

        # enable plugin in contrail settings
        self.activate_plugin()

        self.deploy_cluster()

        # create net and subnet
        self.create_net_subnet(self.cluster_id)

        #  add 1 node with controller and 1 node with
        # compute role and redeploy cluster
        self.fuel_web.update_nodes(
            self.cluster_id, {
                'slave-04': ['base-os'],
                'slave-05': ['base-os']},
            contrail=True
        )

        self.deploy_cluster()

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
                              ('Launch instance with file injection')])

    @test(depends_on=[SetupEnvironment.prepare_slaves_9],
          groups=["deploy_ha_with_vlan_tagging"])
    @log_snapshot_after_test
    def deploy_ha_with_vlan_tagging(self):
        """Verify deploy Contrail Plugin with vlan tagging

        Scenario:
            1. Revert snapshot "ready_with_9_slaves"
            2. Create cluster
            3. Use VLAN tagging for storage and management section
            4. Add 3 nodes with Operating system role,
                2 nodes with controller role and 2 nodes with compute role
            5. Enable Contrail plugin
            6. Deploy cluster with plugin
            7. Deploy cluster
            8. Run OSTF tests

        Duration 140 min

#        :return:
        """

        self.prepare_contrail_plugin(slaves=9)

        networking_parameters = self.fuel_web.client.get_networks(
            self.cluster_id)

        tags = {'storage': 101, 'management': 102}

        for name in networking_parameters["networks"]:
            for k in tags.keys():
                if k == str(name['name']):
                    name['vlan_start'] = tags[k]

        self.fuel_web.client.update_network(self.cluster_id)

        self.fuel_web.update_nodes(
            self.cluster_id,
            {
                'slave-01': ['base-os'],
                'slave-02': ['base-os'],
                'slave-03': ['base-os'],
                'slave-04': ['controller'],
                'slave-05': ['controller'],
                'slave-06': ['compute'],
                'slave-07': ['compute'],
            },
            contrail=True
        )

        # configure disks on base-os nodes
        self.change_disk_size()

        # enable plugin in contrail settings
        self.activate_plugin()

        # deploy cluster
        self.deploy_cluster()

        # create net and subnet
        self.create_net_subnet(self.cluster_id)

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
          groups=["contrail_mu"])
    @log_snapshot_after_test
    def contrail_mu(self):
        """
        MU test for the build stable general verification

        Scenario:
            1. Revert snapshot "ready_with_9_slaves"
            2. Create cluster
            3. Add 2 nodes with Operating system role and
               1 node with controller role
            4. Enable Contrail plugin
            5. Deploy cluster with plugin
            6. Add 1 node with compute role, 1 node with controller,
               1 node with base-os
            7. Deploy cluster
            8. Run OSTF tests
            9. Add 2 nodes with compute role and
               1 node with controller role
            10. Deploy cluster
            11. Run OSTF tests
            12. Remove 2 nodes with controller role.
            13. Deploy cluster
            14. Add 2 nodes with controller role
            15. Deploy cluster
            16. Run OSTF tests
            17. Remove 2 nodes with compute role.
            18. Deploy cluster
            19. Add 2 nodes with compute role
            20. Deploy cluster
            21. Run OSTF tests
        Duration 180 min

        :return:
        """

        self.prepare_contrail_plugin(slaves=9)

        logger.info("first verify ha with Contrail Plugin")

        logger.info("The 1st deployment: create cluster with 2 nodes "
                    "with Operating system role and 1 node with controller role")
        self.fuel_web.update_nodes(
            self.cluster_id,
            {
                'slave-01': ['base-os'],
                'slave-02': ['base-os'],
                'slave-03': ['controller'],
            },
            contrail=True
        )

        # configure disks on base-os nodes
        self.change_disk_size()

        # enable plugin in contrail settings
        self.activate_plugin()

        self.deploy_cluster()

        # create net and subnet
        self.create_net_subnet(self.cluster_id)

        logger.info("The 2nd deployment: add 1 node with compute role, "
                    "1 node with controller, 1 node with base-os and redeploy cluster")
        self.fuel_web.update_nodes(
            self.cluster_id, {'slave-04': ['compute', 'cinder'],
                              'slave-05': ['controller'],
                              'slave-06': ['base-os']}
            )

        self.deploy_cluster()

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

        logger.info("The 3rd deployment: add to cluster 2 nodes with compute role"
                    " and one with controller role and deploy cluster")
        self.fuel_web.update_nodes(
            self.cluster_id,
            {
                'slave-07': ['controller'],
                'slave-08': ['compute'],
                'slave-09': ['compute', 'cinder'],
            }
        )

        logger.info(self.ostf_msg)

        self.deploy_cluster()

        #TODO
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

        logger.info("verify that Controller's nodes can be deleted and added after deploy")

        logger.info("The 4th deployment: remove 2 nodes with controller role")
        self.fuel_web.update_nodes(
            self.cluster_id, {'slave-03': ['controller'],
                              'slave-05': ['controller']
                              }, False, True)

        self.deploy_cluster()

        logger.info("The 5th deployment: add them back and redeploy cluster")
        self.fuel_web.update_nodes(
            self.cluster_id, {'slave-03': ['controller'],
                              'slave-05': ['controller']
                              })

        self.deploy_cluster()

        # TODO
        # Tests using north-south connectivity are expected to fail because
        # they require additional gateway nodes, and specific contrail
        # settings. This mark is a workaround until it's verified
        # and tested manually.
        # Also workaround according to bug 1457515
        # When it will be done 'should_fail=3' and
        # 'failed_test_name' parameter should be removed.

        self.fuel_web.run_ostf(
            cluster_id=self.cluster_id,
            should_fail=3,
            failed_test_name=[('Check network connectivity '
                               'from instance via floating IP'),
                              ('Launch instance with file injection'),
                              ('Check that required services are running')]
        )

        logger.info("verify that Compute node can be deleted and added after deploying")

        logger.info("The 6th deployment: remove two nodes with compute role and deploy this changes")
        self.fuel_web.update_nodes(
            self.cluster_id, {'slave-04': ['compute', 'cinder'],
                              'slave-08': ['compute']
                              }, False, True)

        self.deploy_cluster()

        logger.info("The 7th deployment: add 2 nodes with compute role and redeploy cluster")
        self.fuel_web.update_nodes(
            self.cluster_id, {'slave-04': ['compute', 'cinder'],
                              'slave-08': ['compute']
                              })

        self.deploy_cluster()

        # TODO
        # Tests using north-south connectivity are expected to fail because
        # they require additional gateway nodes, and specific contrail
        # settings. This mark is a workaround until it's verified
        # and tested manually.
        # Also workaround according to bug 1457515
        # When it will be done 'should_fail=3' and
        # 'failed_test_name' parameter should be removed.

        self.fuel_web.run_ostf(
            cluster_id=self.cluster_id,
            should_fail=3,
            failed_test_name=[('Check network connectivity '
                               'from instance via floating IP'),
                              ('Launch instance with file injection'),
                              ('Check that required services are running')]
        )

    @test(depends_on=[SetupEnvironment.prepare_slaves_5],
          groups=["deploy_contrail_with_ceilometer"])
    @log_snapshot_after_test
    def deploy_contrail_with_ceilometer(self):
        """Verify deploy correctness with the same Contrail Controllers names

        Scenario:
            1. Revert snapshot "ready_with_5_slaves"
            2. Create cluster
            3. Add 3 nodes with Operating system role,
                1 node with controller role + "Telemetry Mongo DB"
                and 1 node with compute role
            4. Enable Contrail plugin
            5. Deploy cluster with plugin
            6. Deploy cluster
            7. Run OSTF tests

        Duration 140 min

#        :return:
        """
        self.prepare_contrail_plugin(slaves=5)

        # create cluster: 3 nodes with Operating system role,
        # 1 node with controller + "Telemetry Mongo DB"
        # and 1 node with compute roles
        self.fuel_web.update_nodes(
            self.cluster_id,
            {
                'slave-01': ['base-os'],
                'slave-02': ['base-os'],
                'slave-03': ['base-os'],
                'slave-04': ['controller', 'mongo'],
                'slave-05': ['compute'],
            },
            contrail=True
        )

        # configure disks on base-os nodes
        self.change_disk_size()

        # enable plugin in contrail settings
        self.activate_plugin()

        self.deploy_cluster()

        # create net and subnet
        self.create_net_subnet(self.cluster_id)

        #TODO
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
          groups=["deploy_contrail_with_base_os_ceph"])
    @log_snapshot_after_test
    def deploy_contrail_with_base_os_ceph(self):
        """Verify deploy Contrail cluster with Ceph on Compute nodes

        Scenario:
            1. Revert snapshot "ready_with_9_slaves"
            2. Select 'Use Ceph' in Storage Backends
            3. Create cluster
            4. Add 3 nodes with Operating system role,
               1 node with controller role and 2 nodes with
               compute + 'Storage-Ceph OSD' role
            5. Enable Contrail plugin
            6. Deploy cluster with plugin
            7. Deploy cluster
            8. Run OSTF tests

        Duration 140 min

#        :return:
        """
        self.prepare_contrail_plugin(slaves=9, ceph_value=True)

        # create cluster: 3 nodes with Operating system role and 1 node with
        # controller role and 2 nodes with compute + ceph OSD role
        self.fuel_web.update_nodes(
            self.cluster_id,
            {
                'slave-01': ['base-os'],
                'slave-02': ['base-os'],
                'slave-03': ['base-os'],
                'slave-04': ['controller'],
                'slave-05': ['compute', 'ceph-osd'],
                'slave-06': ['compute', 'ceph-osd'],
            },
            contrail=True
        )

        # configure disks on base-os nodes
        self.change_disk_size()

        # enable plugin in contrail settings
        self.activate_plugin()

        self.deploy_cluster()

        # create net and subnet
        self.create_net_subnet(self.cluster_id)

         #TODO
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

    @test(depends_on=[SetupEnvironment.prepare_slaves_5],
          groups=["contrail_jumbo_frame"])
    @log_snapshot_after_test
    def contrail_jumbo_frame(self):
        """Deploy Contrail cluster with jumbo frames enabled for Private
        network

        Scenario:
            1. Revert snapshot "ready_with_5_slaves"
            2. Create cluster
            4. Add 3 nodes with Operating system role, 1 node with controller
               role and 1 node with compute role
            5. Configure network and set mtu 9000 for private network
            6. Enable Contrail plugin
            7. Deploy cluster
            8. Run OSTF tests

        Duration 140 min

#        :return:
        """

        self.prepare_contrail_plugin(slaves=5)

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

        self.fuel_web.update_nodes(
            self.cluster_id,
            {
                'slave-01': ['base-os'],
                'slave-02': ['base-os'],
                'slave-03': ['base-os'],
                'slave-04': ['controller'],
                'slave-05': ['compute'],
            },
            contrail=True
        )

        slave_nodes = self.fuel_web.client.list_cluster_nodes(self.cluster_id)
        for node in slave_nodes:
            self.fuel_web.update_node_networks(
                node['id'], interfaces,
                override_ifaces_params=interfaces_update)

        # configure disks on base-os nodes
        self.change_disk_size()

        # enable plugin in contrail settings
        self.activate_plugin()

        self.deploy_cluster()

        # create net and subnet
        self.create_net_subnet(self.cluster_id)

        #TODO
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
