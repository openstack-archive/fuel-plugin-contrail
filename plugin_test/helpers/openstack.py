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
from fuelweb_test import logger
from fuelweb_test.settings import DEPLOYMENT_MODE
from fuelweb_test.helpers.checkers import check_repo_managment
import openstack


def assign_net_provider(obj, **options):
    """Assign neutron with tunneling segmentation"""
    available_params = [
        'assign_to_all_nodes', 'images_ceph', 'volumes_ceph',
        'ephemeral_ceph', 'objects_ceph', 'volumes_lvm'
    ]
    assert all(p in available_params for p in options), \
        'Invalid params for func %s' % options
    default_settings = {
        "net_provider": 'neutron',
        "net_segment_type": 'tun',
        "assign_to_all_nodes": False,
        "images_ceph": False,
        "volumes_ceph": False,
        "ephemeral_ceph": False,
        "objects_ceph": False,
        "volumes_lvm": True
    }
    default_settings.update(options)
    obj.cluster_id = obj.fuel_web.create_cluster(
        name=obj.__class__.__name__,
        mode=DEPLOYMENT_MODE,
        settings=default_settings)
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


def assign_vlan(obj, **interface_tags):
    """ Configure vlan on interfaces
    :param obj: Test case object
    :param interface_tags: keyword params of interface role and it's vlan tags
    :return: None
    """
    nets = obj.fuel_web.client.get_networks(obj.cluster_id)['networks']
    for net in nets:
        if net['name'] in interface_tags.keys():
            net['vlan_start'] = interface_tags[net['name']]
    obj.fuel_web.client.update_network(obj.cluster_id, networks=nets)


def update_deploy_check(obj, nodes, delete=False, is_vsrx=True):
    # Cluster configuration
    obj.fuel_web.update_nodes(obj.cluster_id,
                              nodes_dict=nodes,
                              pending_addition=not delete,
                              pending_deletion=delete)
    # deploy cluster
    openstack.deploy_cluster(obj)

    # FIXME: remove next line when bug #1516969 will be fixed
    time.sleep(60*25)

    # Run OSTF tests
    if is_vsrx:
        obj.fuel_web.run_ostf(cluster_id=obj.cluster_id)
