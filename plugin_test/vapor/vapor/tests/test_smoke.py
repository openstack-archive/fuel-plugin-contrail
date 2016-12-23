# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from hamcrest import (assert_that, empty, has_item, has_entry, is_not,
                      has_property)  # noqa H301
import pycontrail.types as types
import pytest
from stepler.third_party import utils


def test_contrail_node_services_status(contrail_nodes, os_faults_steps):
    cmd = "contrail-status | grep -Pv '(==|^$)'"
    broken_services = []
    for node_result in os_faults_steps.execute_cmd(contrail_nodes, cmd):
        for line in node_result.payload['stdout_lines']:
            values = line.strip().split(None, 1)
            if len(values) < 2:
                continue
            name, status = values
            if status not in {'active', 'backup'}:
                err_msg = "{node}:{service} - {status}".format(
                    node=node_result.host, service=name, status=status)
                broken_services.append(err_msg)
    assert_that(broken_services, empty())


def test_contrail_on_compute(os_faults_steps):
    compute_cmd = 'ps ax| grep compute | grep -v grep'
    check_cmd = "contrail-status | grep -Pv '(==|^$)'"
    expected_services = ['supervisor-vrouter',
                         'contrail-vrouter-agent',
                         'contrail-vrouter-nodemgr']
    broken_services = []
    compute_nodes = os_faults_steps.get_nodes_by_cmd(compute_cmd)
    for node_result in os_faults_steps.execute_cmd(compute_nodes, check_cmd):
        for line in node_result.payload['stdout_lines']:
            values = line.strip().split(None, 1)
            if len(values) < 2:
                continue
            name, status = values
            if name in expected_services and status not in {'active', 'backup'}:
                err_msg = "{node}:{service} - {status}".format(
                    node=node_result.host, service=name, status=status)
                broken_services.append(err_msg)

            print('values:%s' % str(values))
    assert_that(broken_services, empty())


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
