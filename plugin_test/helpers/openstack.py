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
import time
from fuelweb_test import logger
from fuelweb_test.settings import DEPLOYMENT_MODE
from fuelweb_test.helpers.checkers import check_repo_managment


def assign_net_provider(obj, **options):
    """Assign neutron with tunneling segmentation"""
    available_params = ['pub_all_nodes', 'ceph_value', 'volumes_ceph', 'ephemeral_ceph', 'objects_ceph', 'volumes_lvm']
    assert all(p in available_params for p in options), 'Invalid params for func %s' % options
    settings = {
        "net_provider": 'neutron',
        "net_segment_type": 'tun',
        "assign_to_all_nodes": False,
        "images_ceph": False,
        "volumes_ceph": False,
        "ephemeral_ceph": False,
        "objects_ceph": False,
        "volumes_lvm": False
    }
    settings.update(options)
    obj.cluster_id = obj.fuel_web.create_cluster(
        name=obj.__class__.__name__,
        mode=DEPLOYMENT_MODE,
        settings=settings)
    return obj.cluster_id


def deploy_cluster(obj):
    """
    Deploy cluster with additional time for waiting on node's availability
    """
    try:
        obj.fuel_web.deploy_cluster_wait(
            obj.cluster_id, check_services=False)
    except:
        nailgun_nodes = obj.env.fuel_web.client.list_cluster_nodes(
            obj.env.fuel_web.get_last_created_cluster())
        time.sleep(420)
        for n in nailgun_nodes:
            check_repo_managment(
                obj.env.d_env.get_ssh_to_remote(n['ip']))
            logger.info('ip is {0}'.format(n['ip'], n['name']))
