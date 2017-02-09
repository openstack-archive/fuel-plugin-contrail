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
                      has_property, has_entries, has_items)  # noqa H301
import jmespath
import pycontrail.types as types
import pytest
from stepler.third_party import utils

from vapor.helpers import contrail_status
from vapor import settings


def test_contrail_node_services_status(os_faults_steps):
    contrail_status.check_services_statuses(os_faults_steps)


@pytest.mark.parametrize('role', settings.CONTRAIL_ROLES_DISTRIBUTION)
def test_contrail_service_distribution(os_faults_steps, role):
    services_statuses = contrail_status.get_services_statuses(os_faults_steps)
    statuses = {
        node: service.service
        for node, services in services_statuses.items() for service in services
    }
    services = settings.CONTRAIL_ROLES_SERVICES_MAPPING[role]
    nodes = settings.CONTRAIL_ROLES_DISTRIBUTION[role]
    entries = {node: has_items(*services) for node in nodes}
    assert_that(statuses, has_entries(**entries))


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
