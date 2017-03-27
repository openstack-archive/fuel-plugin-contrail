# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from hamcrest import (assert_that, has_item, has_entry, is_not, empty,
                      has_property, contains_inanyorder)  # noqa: H301
import jmespath
import pycontrail.types as types
import pytest
from stepler.third_party import utils
from stepler.third_party import waiter

from vapor.helpers import contrail_status
from vapor.helpers import asserts
from vapor.helpers.asserts import superset_of
from vapor import settings


def test_contrail_node_services_status(os_faults_steps):
    contrail_status.check_services_statuses(os_faults_steps)


@pytest.mark.parametrize('role', settings.CONTRAIL_ROLES_DISTRIBUTION)
def test_contrail_service_distribution(os_faults_steps, role):
    """Check that contrail services are running on correct nodes."""
    services_statuses = contrail_status.get_services_statuses(os_faults_steps)
    nodes = settings.CONTRAIL_ROLES_DISTRIBUTION[role]
    expected_services = settings.CONTRAIL_ROLES_SERVICES_MAPPING[role]
    with asserts.AssertsCollector() as collector:
        for node, services in services_statuses.items():
            if node not in nodes:
                continue
            services = [x.service for x in services]
            collector.check(services, superset_of(expected_services))


def test_ifmap_service(os_faults_steps):
    """Verify ifmap service."""
    fqdns = settings.CONTRAIL_ROLES_DISTRIBUTION[
        settings.ROLE_CONTRAIL_CONTROLLER]
    nodes = os_faults_steps.get_nodes(fqdns)
    os_faults_steps.execute_cmd(nodes, 'ifmap-view visual visual')


@pytest.mark.usefixtures('contrail_network_cleanup')
def test_add_virtual_network(contrail_api_client):
    network_name, = utils.generate_ids()
    net = types.VirtualNetwork(network_name)
    contrail_api_client.virtual_network_create(net)
    networks = contrail_api_client.virtual_networks_list()
    assert_that(networks['virtual-networks'],
                has_item(has_entry('uuid', net.uuid)))


@pytest.mark.usefixtures('contrail_network_cleanup')
def test_delete_virtual_network(contrail_api_client, contrail_network):
    contrail_api_client.virtual_network_delete(id=contrail_network.uuid)
    networks = contrail_api_client.virtual_networks_list()
    assert_that(networks['virtual-networks'],
                is_not(has_item(has_entry('uuid', contrail_network.uuid))))


@pytest.mark.usefixtures('contrail_network_cleanup')
def test_update_virtual_network(contrail_api_client, contrail_network):
    new_display_name, = utils.generate_ids()
    contrail_network.display_name = new_display_name
    contrail_api_client.virtual_network_update(contrail_network)
    network_data = contrail_api_client.virtual_network_read(
        id=contrail_network.uuid)
    assert_that(network_data, has_property('display_name', new_display_name))


@pytest.mark.usefixtures('contrail_security_groups_cleanup')
def test_add_security_group(contrail_api_client):
    security_group_name, = utils.generate_ids()
    security_group = types.SecurityGroup(security_group_name)
    contrail_api_client.security_group_create(security_group)
    groups = contrail_api_client.security_groups_list()
    assert_that(groups['security-groups'],
                has_item(has_entry('uuid', security_group.uuid)))


@pytest.mark.usefixtures('contrail_security_groups_cleanup')
def test_delete_security_group(contrail_api_client, contrail_security_group):
    contrail_api_client.security_group_delete(id=contrail_security_group.uuid)
    groups = contrail_api_client.security_groups_list()
    assert_that(
        groups['security-groups'],
        is_not(has_item(has_entry('uuid', contrail_security_group.uuid))))


@pytest.mark.usefixtures('contrail_security_groups_cleanup')
def test_update_security_group(contrail_api_client, contrail_security_group):
    new_display_name, = utils.generate_ids()
    contrail_security_group.display_name = new_display_name
    contrail_api_client.security_group_update(contrail_security_group)
    group_data = contrail_api_client.security_group_read(
        id=contrail_security_group.uuid)
    assert_that(group_data, has_property('display_name', new_display_name))


@pytest.mark.usefixtures('contrail_policies_cleanup')
def test_add_network_policy(contrail_api_client):
    network_policy_name, = utils.generate_ids()
    network_policy = types.NetworkPolicy(network_policy_name)
    contrail_api_client.network_policy_create(network_policy)
    policies = contrail_api_client.network_policys_list()
    assert_that(policies['network-policys'],
                has_item(has_entry('uuid', network_policy.uuid)))


@pytest.mark.usefixtures('contrail_policies_cleanup')
def test_delete_network_policy(contrail_api_client, contrail_network_policy):
    contrail_api_client.network_policy_delete(id=contrail_network_policy.uuid)
    policies = contrail_api_client.network_policys_list()
    assert_that(
        policies['network-policys'],
        is_not(has_item(has_entry('uuid', contrail_network_policy.uuid))))


@pytest.mark.usefixtures('contrail_policies_cleanup')
def test_update_network_policy(contrail_api_client, contrail_network_policy):
    new_display_name, = utils.generate_ids()
    contrail_network_policy.display_name = new_display_name
    contrail_api_client.network_policy_update(contrail_network_policy)
    policy_data = contrail_api_client.network_policy_read(
        id=contrail_network_policy.uuid)
    assert_that(policy_data, has_property('display_name', new_display_name))


@pytest.mark.usefixtures('contrail_ipams_cleanup')
def test_add_network_ipam(contrail_api_client):
    network_ipam_name, = utils.generate_ids()
    network_ipam = types.NetworkIpam(network_ipam_name)
    contrail_api_client.network_ipam_create(network_ipam)
    ipams = contrail_api_client.network_ipams_list()
    assert_that(ipams['network-ipams'],
                has_item(has_entry('uuid', network_ipam.uuid)))


@pytest.mark.usefixtures('contrail_ipams_cleanup')
def test_delete_network_ipam(contrail_api_client, contrail_ipam):
    contrail_api_client.network_ipam_delete(id=contrail_ipam.uuid)
    ipams = contrail_api_client.network_ipams_list()
    assert_that(
        ipams['network-ipams'],
        is_not(has_item(has_entry('uuid', contrail_ipam.uuid))))


@pytest.mark.usefixtures('contrail_ipams_cleanup')
def test_update_network_ipam(contrail_api_client, contrail_ipam):
    new_display_name, = utils.generate_ids()
    contrail_ipam.display_name = new_display_name
    contrail_api_client.network_ipam_update(contrail_ipam)
    ipam_data = contrail_api_client.network_ipam_read(
        id=contrail_ipam.uuid)
    assert_that(ipam_data, has_property('display_name', new_display_name))


def test_contrail_alarms_is_empty(client_contrail_analytics):
    alarms = client_contrail_analytics.get_alarms()
    query = ('*[?@.value.*.alarms[?ack!=`True`]][].'
             '{Node: @.name, Type: @.value.*.alarms[].type}')
    not_ack_alarms = jmespath.search(query, alarms)
    assert_that(not_ack_alarms, empty())


def test_zookeeper_status(znodes_list):
    expected_znodes_list = settings.ZOOKEEPER_NODES
    assert_that(znodes_list, contains_inanyorder(*expected_znodes_list))


@pytest.mark.requires('contrail_control_nodes_count >= 2')
def test_contrail_services_status_after_restart_master_node(os_faults_steps):
    """Verify contrail services status after master node restart.

    Steps:
        #. Restart node with contrail-schema (active)
        #. Wait some time
        #. Check that contrail services statuses is correct
    """
    services_statuses = contrail_status.get_services_statuses(os_faults_steps)
    master_node_fqdn = None
    for fqdn, services in services_statuses.items():
        for service in services:
            if (service['service'] == 'contrail-schema' and
                    service['status'] == contrail_status.STATUS_ACTIVE):
                master_node_fqdn = fqdn
                break
    assert master_node_fqdn is not None, "Can't find master node"
    master_node = os_faults_steps.get_node(fqdns=[master_node_fqdn])
    os_faults_steps.reset_nodes(master_node)

    waiter.wait(
        contrail_status.check_services_statuses,
        args=(os_faults_steps),
        expected_exceptions=AssertionError,
        timeout=settings.CONTRAIL_NODE_RESET_TIMEOUT)
