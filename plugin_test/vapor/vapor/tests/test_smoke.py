# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from hamcrest import (assert_that, has_item, has_entry, is_not, equal_to,
                      has_property)  # noqa H301
import pycontrail.types as types
import pytest
from stepler.third_party import utils

from vapor.helpers import contrail_status
from vapor import settings


def test_contrail_node_services_status(os_faults_steps):
    contrail_status.check_services_statuses(os_faults_steps)


@pytest.mark.parametrize('service',
                         settings.CONRTAIL_SERVICES_DISTRIBUTION)
def test_contrail_service_distribution(os_faults_steps, service):
    statuses = contrail_status.get_services_statuses(os_faults_steps)
    expected = set(settings.CONRTAIL_SERVICES_DISTRIBUTION[service])
    actual = set()
    for node, services in statuses.items():
        if service in services:
            actual.add(node)
    assert_that(actual, equal_to(expected))


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
