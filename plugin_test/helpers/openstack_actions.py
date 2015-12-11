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

import time
from probocis import test
from fuelweb_test import logger
from fuelweb_test.settings import DEPLOYMENT_MODE
from fuelweb_test.helpers.checkers import check_repo_managment


@test(groups=["plugins"])
class OpenstackActions(object):
    """Methods for openstack actions"""

    def assign_net_provider(self, pub_all_nodes=False, ceph_value=False):
        """Assign neutron with tunneling segmentation"""
        segment_type = 'tun'
        cluster_id = self.fuel_web.create_cluster(
            name=self.__class__.__name__,
            mode=DEPLOYMENT_MODE,
            settings={
                "net_provider": 'neutron',
                "net_segment_type": segment_type,
                "assign_to_all_nodes": pub_all_nodes,
                "images_ceph": ceph_value
            }
        )
        return cluster_id


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
