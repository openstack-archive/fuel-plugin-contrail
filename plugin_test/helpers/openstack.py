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

import time

from devops.helpers.helpers import wait
from fuelweb_test import logger
from fuelweb_test.settings import DEPLOYMENT_MODE
from fuelweb_test.settings import HARDWARE
from fuelweb_test.helpers.checkers import check_repo_managment

import settings
from tests import test_contrail_check


def assign_net_provider(obj, **options):
    """Assign neutron with tunneling segmentation."""
    default_settings = {
        "net_provider": 'neutron',
        "net_segment_type": 'tun',
        "assign_to_all_nodes": False,
        "images_ceph": False,
        "volumes_ceph": False,
        "ephemeral_ceph": False,
        "objects_ceph": False,
        "volumes_lvm": True,
        "ceilometer": False,
        "sahara": False,
        "murano": False,
        "osd_pool_size": '3'
    }

    if "assert_deny" not in options:
        assert all(p in default_settings.keys() for p in options), \
            'Invalid params for func %s' % options
    else:
        del options["assert_deny"]

    default_settings.update(options)
    obj.cluster_id = obj.fuel_web.create_cluster(
        name=obj.__class__.__name__,
        mode=DEPLOYMENT_MODE,
        settings=default_settings)

    # Configure private network (disable vlan and etc.)
    nets = obj.fuel_web.client.get_networks(obj.cluster_id)['networks']
    for net in nets:
        if net['name'] == 'private':
            net['ip_ranges'][0][0] = net['ip_ranges'][0][0][:-1] + '2'
            net['vlan_start'] = None
            net['meta']['notation'] = 'ip_ranges'
    obj.fuel_web.client.update_network(obj.cluster_id, networks=nets)

    return obj.cluster_id


def deploy_cluster(obj, wait_for_status='operational'):
    """Deploy cluster with additional time for waiting on node's availability.

    :param obj: Test case object
    :param wait_for_status: status of deployment
    """
    try:
        obj.fuel_web.deploy_cluster_wait(
            obj.cluster_id, check_services=False,
            timeout=180 * 60)
    except Exception:
        nailgun_nodes = obj.env.fuel_web.client.list_cluster_nodes(
            obj.env.fuel_web.get_last_created_cluster())
        time.sleep(420)
        for n in nailgun_nodes:
            check_repo_managment(
                obj.env.d_env.get_ssh_to_remote(n['ip']))
            logger.info('ip is {0}'.format(n['ip'], n['name']))
    if wait_for_status:
        wait_for_cluster_status(obj, obj.cluster_id,
                                status=wait_for_status)


def assign_vlan(obj, **interface_tags):
    """Configure vlan on interfaces.

    :param obj: Test case object
    :param interface_tags: keyword params of interface role and it's vlan tags
    :return: None
    """
    nets = obj.fuel_web.client.get_networks(obj.cluster_id)['networks']
    for net in nets:
        if net['name'] in interface_tags.keys():
            net['vlan_start'] = interface_tags[net['name']]
    obj.fuel_web.client.update_network(obj.cluster_id, networks=nets)


def update_deploy_check(obj, nodes, delete=False, is_vsrx=True,
                        ostf_timeout=settings.OSTF_RUN_TIMEOUT,
                        ostf_suites=[], ostf_fail_tests=[]):
    """Update, deploy and check cluster.

    :param obj: Test case object
    :param nodes:type dictionary, dictionary of nodes
    :param delete: type boolean, True if node should be deleted
    :param is_vsrx: type booleam, doesn't run tests if vsrx is not set
    :param ostf_timeout: timeout for tests
    :param ostf_suites: test suites to run
    :param ostf_fail_tests: tests which should fails
    """
    # Cluster configuration
    obj.fuel_web.update_nodes(obj.cluster_id,
                              nodes_dict=nodes,
                              pending_addition=not delete,
                              pending_deletion=delete)
    # deploy cluster
    deploy_cluster(obj)

    # Run OSTF tests
    if is_vsrx:
        ostf_params = {}
        if ostf_timeout:
            ostf_params['timeout'] = ostf_timeout
        if ostf_suites:
            ostf_params['test_sets'] = ostf_suites
        if ostf_fail_tests:
            ostf_params['should_fail'] = len(ostf_fail_tests)
            ostf_params['failed_test_name'] = ostf_fail_tests
        obj.fuel_web.run_ostf(cluster_id=obj.cluster_id, **ostf_params)

        test_contrail_check.TestContrailCheck(obj).cloud_check(['contrail'])


def wait_for_cluster_status(obj, cluster_id,
                            status='operational',
                            timeout=settings.DEPLOY_CLUSTER_TIMEOUT):
    """Wait for cluster status until timeout is reached.

    :param obj: Test case object, usually it is 'self'
    :param cluster_id: cluster identifier
    :param status: Cluster status, available values:

      - new
      - deployment
      - stopped
      - operational
      - error
      - remove
      - update
      - update_error
    :param timeout: the time that we are waiting.
    :return: time that we are actually waited.

    """
    def check_func():
        for c in obj.fuel_web.client.list_clusters():
            if c['id'] == cluster_id and c['status'] == status:
                return True
        return False
    wtime = wait(check_func, interval=30, timeout=timeout)
    logger.info('Wait cluster id:"{}" deploy done in {}sec.'.format(cluster_id,
                                                                    wtime))
    return wtime


def enable_sriov(obj):
    """Activate SRiOV interface on baremetal node.

    :param obj: Test case object, usually it is 'self'

    """
    assign_vlan(obj, storage=102, management=101)
    node_mac = obj.bm_drv.conf['target_macs']
    nailgun_node = obj.bm_drv.get_bm_node(obj, node_mac)
    node_assighned_interfaces = [
        intr['dev'] for intr in nailgun_node['network_data']]
    node_networks = obj.fuel_web.client.get_node_interfaces(
        nailgun_node['id'])
    for interface in node_networks:
        if interface['name'] not in node_assighned_interfaces:
            interface['interface_properties']['sriov']['enabled'] = True
            interface['interface_properties']['sriov']['sriov_numvfs'] = \
                interface['interface_properties']['sriov']['sriov_totalvfs']
    obj.fuel_web.client.put_node_interfaces(
        [{'id': nailgun_node['id'], 'interfaces': node_networks}])


def check_slave_memory(min_memory):
    """Check memory on slave."""
    if HARDWARE["slave_node_memory"] < min_memory:
        error_msg = 'Out of slaves ram'
        logger.warning(error_msg)
        return False
    else:
        msg = 'Slaves have {0} mb ram'.format(HARDWARE["slave_node_memory"])
        logger.info(msg)
        return True


def setup_hugepages(obj, hp_2mb=512, hp_1gb=30, hp_dpdk_mb=0):
    """Set value of huge page on dpdk node."""
    node_mac = obj.bm_drv.conf['target_macs']
    nailgun_node = obj.bm_drv.get_bm_node(obj, node_mac)
    node_attributes = obj.fuel_web.client.get_node_attributes(
        nailgun_node['id'])
    node_attributes['hugepages']['nova']['value']['2048'] = hp_2mb
    node_attributes['hugepages']['nova']['value']['1048576'] = hp_1gb
    node_attributes['hugepages']['dpdk']['value'] = hp_dpdk_mb
    obj.fuel_web.client.upload_node_attributes(node_attributes,
                                                    nailgun_node['id'])
