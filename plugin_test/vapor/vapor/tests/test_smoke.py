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
from stepler.third_party import utils


def test_contrail_node_services_status(contrail_nodes, os_faults_steps):
    cmd = "contrail-status | grep -Pv '(==|^$)'"
    broken_services = []
    for node_result in os_faults_steps.execute_cmd(contrail_nodes, cmd):
        for line in node_result.payload['stdout_lines']:
            line = line.strip()
            name, status = line.split(None, 1)
            if status not in {'active', 'backup'}:
                err_msg = "{node}:{service} - {status}".format(
                    node=node_result.host, service=name, status=status)
                broken_services.append(err_msg)
    assert_that(broken_services, empty())


def test_add_virtual_network(contrail_api_client):
    network_name, = utils.generate_ids()
    net = types.VirtualNetwork(network_name)
    contrail_api_client.virtual_network_create(net)
    networks = contrail_api_client.virtual_networks_list()
    assert_that(networks['virtual-networks'],
                has_item(has_entry('uuid', net.uuid)))


def test_delete_virtual_network(contrail_api_client, network):
    contrail_api_client.virtual_network_delete(id=network.uuid)
    networks = contrail_api_client.virtual_networks_list()
    assert_that(networks['virtual-networks'],
                is_not(has_item(has_entry('uuid', network.uuid))))


def test_update_virtual_network(contrail_api_client, network):
    new_display_name, = utils.generate_ids()
    network.display_name = new_display_name
    contrail_api_client.virtual_network_update(network)
    network_data = contrail_api_client.virtual_network_read(id=network.uuid)
    assert_that(network_data, has_property('display_name', new_display_name))


def test_add_security_group(contrail_api_client):
    security_group_name, = utils.generate_ids()
    security_group = types.SecurityGroup(security_group_name)
    contrail_api_client.security_group_create(security_group)
    groups = contrail_api_client.security_groups_list()
    assert_that(groups['security-groups'],
                has_item(has_entry('uuid', security_group.uuid)))


def test_delete_security_group(contrail_api_client, security_group):
    contrail_api_client.security_group_delete(id=security_group.uuid)
    groups = contrail_api_client.security_groups_list()
    assert_that(groups['security-groups'],
                is_not(has_item(has_entry('uuid', security_group.uuid))))


def test_update_security_group(contrail_api_client, security_group):
    new_display_name, = utils.generate_ids()
    security_group.display_name = new_display_name
    contrail_api_client.security_group_update(security_group)
    group_data = contrail_api_client.security_group_read(
        id=security_group.uuid)
    assert_that(group_data, has_property('display_name', new_display_name))
