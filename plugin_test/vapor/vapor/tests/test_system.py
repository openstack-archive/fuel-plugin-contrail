# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import itertools
import time

from hamcrest import (assert_that, has_length, has_items, has_entries,
                      equal_to, is_not, empty)
import pycontrail.client as client
from pycontrail import exceptions
import pytest
from stepler import config as stepler_config
from stepler.third_party import ping
from stepler.third_party import utils
from stepler.third_party import waiter

from vapor.helpers import contrail_steps
from vapor.helpers import nodes_steps
from vapor.helpers import policy
from vapor import settings


def test_no_connectivity_between_vms_in_different_tenants(
        request, contrail_api_client, os_faults_steps):
    """Check no connectivity between VMs in different tenants.

    Steps:
        #. Create 2 new tenants (the tenant networks under test must have
            intersecting or the same IP address spaces and the must be no
            policy enabled, which allows the traffic between tenants)
        #. Launch 2 new instance in different tenants
        #. Check that no ping connectivity between instances
        #. Connect to Compute Node via SSH and check that VMs has different
            ethernet device
        #. Verify with contrail API that networks are present and VMs are
            attached to different networks.
    """
    # Store nodes interfaces
    before_interfaces = nodes_steps.get_nodes_interfaces(os_faults_steps)

    resources = request.getfixturevalue('different_tenants_resources')
    # Check that there is no ping between tenants
    for resources1, resources2 in itertools.permutations(resources):
        ip_to_ping = resources1.server_steps.get_fixed_ip(resources1.server)
        server_steps = resources2.server_steps
        floating_ip = resources2.floating_ip['floating_ip_address']
        with server_steps.get_server_ssh(
                resources2.server, ip=floating_ip) as server_ssh:
            with server_steps.check_no_ping_context(
                    ip_to_ping, server_ssh=server_ssh):
                time.sleep(5)

    # Get interfaces list again
    after_interfaces = nodes_steps.get_nodes_interfaces(os_faults_steps)
    compute_fqdn = getattr(resources[0].server,
                           stepler_config.SERVER_ATTR_HOST)

    # Check that there is 2 interfaces on compute - one for each VM
    assert_that(
        after_interfaces[compute_fqdn] - before_interfaces[compute_fqdn],
        has_length(2))

    # Check that networks are present in contrail
    contrail_networks = contrail_api_client.virtual_networks_list()
    networks_matchers = [
        has_entries(uuid=res.network['id']) for res in resources
    ]
    assert_that(contrail_networks['virtual-networks'],
                has_items(*networks_matchers))

    # Check that VMs attached to different networks
    networks_uuid = set()
    for resource in resources:
        iface = contrail_api_client.virtual_machine_interface_read(
            id=resource.port['id'])
        networks_uuid.add(iface.get_virtual_network_refs()[0]['uuid'])
    assert_that(networks_uuid, has_length(2))


def test_create_network_with_contrail(
        cirros_image, flavor, security_group, contrail_network,
        contrail_subnet, public_network, create_floating_ip,
        contrail_api_client, server_steps, port_steps):
    """Check that OpenStack can operate with network created with Contrail.

    Steps:
        #. Create new network with Contrail API
        #. Launch 2 instances on created network
        #. Check ping between instances
        #. Verify that instances are attached to created network in contrail
    """
    servers = server_steps.create_servers(
        count=2,
        image=cirros_image,
        flavor=flavor,
        nics=[{
            'net-id': contrail_network.uuid
        }],
        security_groups=[security_group],
        username=stepler_config.CIRROS_USERNAME,
        password=stepler_config.CIRROS_PASSWORD)
    for server in servers:
        port = port_steps.get_port(
            device_owner=stepler_config.PORT_DEVICE_OWNER_SERVER,
            device_id=server.id)
        floating_ip = create_floating_ip(public_network, port=port)
        server_steps.check_server_ip(
            server,
            floating_ip['floating_ip_address'],
            timeout=settings.FLOATING_IP_BIND_TIMEOUT)

    # Check ping between instances
    server_steps.check_ping_between_servers_via_floating(
        servers, ip_types=(stepler_config.FIXED_IP, ))

    # Verify that instances are attached to created network in contrail
    networks = set()
    for server in servers:
        for net in contrail_steps.get_server_networks(contrail_api_client,
                                                      server.id):
            networks.add(net.uuid)
    assert_that(networks, equal_to(set([contrail_network.uuid])))


@pytest.mark.usefixtures('neutron_network_cleanup')
def test_create_and_terminate_networks(contrail_api_client, network_steps):
    """Create and terminate networks and verify in Contrail.

    Steps:
        #. Create 2 private networks with Neutron
        #. Check that networks is present in Contrail
        #. Delete one of networks with Neutron
        #. Check that deleted network is not present in Contrail
        #. Add private network with Neutron
        #. Check that created network is present in Contrail
    """
    # Create networks
    networks = []
    for name in utils.generate_ids(count=2):
        networks.append(network_steps.create(name))

    # Check networks in contrail
    contrail_networks = contrail_api_client.virtual_networks_list()
    matchers = [has_entries(uuid=network['id']) for network in networks]
    assert_that(contrail_networks['virtual-networks'], has_items(*matchers))

    # Delete network
    network_to_delete = networks.pop()
    network_steps.delete(network_to_delete)

    # Check that deleted network is not present in Contrail
    contrail_networks = contrail_api_client.virtual_networks_list()
    assert_that(
        contrail_networks['virtual-networks'],
        is_not(has_items(has_entries(uuid=network_to_delete['id']))))

    # Create new network
    net_name, = utils.generate_ids()
    new_network = network_steps.create(name)

    # Check that created network is present in Contrail
    contrail_networks = contrail_api_client.virtual_networks_list()
    assert_that(
        contrail_networks['virtual-networks'],
        has_items(has_entries(uuid=new_network['id'])))


def test_networks_connectivity_with_router(
        contrail_2_servers_diff_nets_with_floating, create_router,
        add_router_interfaces, server_steps):
    """Check connectivity on different nodes and different private networks.

    Test with creating router.

    Steps:
        #. Create 2 networks
        #. Launch 2 instances in different network on different computes.
        #. Check that there is no ping between instances.
        #. Create a router betwheen networks.
        #. Check ping between instances.

    """
    resources = contrail_2_servers_diff_nets_with_floating

    # Check ping will fail
    with pytest.raises(Exception):
        server_steps.check_ping_between_servers_via_floating(resources.servers)

    # Create router
    router = create_router(next(utils.generate_ids()))
    add_router_interfaces(router, resources.subnets)

    # Check ping
    server_steps.check_ping_between_servers_via_floating(resources.servers)


def test_network_connectivity_with_policy(
        contrail_2_servers_diff_nets_with_floating, contrail_network_policy,
        set_network_policy, contrail_api_client, server_steps):
    """Check connectivity on different nodes and different private networks.

    Test with creating policy.

    Steps:
        #. Create 2 networks
        #. Launch 2 instances in different network on different computes.
        #. Check that there is no ping between instances.
        #. Connect the networks via Contrail Network Policies.
        #. Check ping between instances.

    """
    resources = contrail_2_servers_diff_nets_with_floating

    # Check ping will fail
    with pytest.raises(Exception):
        server_steps.check_ping_between_servers_via_floating(resources.servers)

    # Update policy
    contrail_network_policy.network_policy_entries = (
        policy.allow_all_policy_entry)
    contrail_api_client.network_policy_update(contrail_network_policy)

    # Bind policy to networks
    for net in resources.networks:
        contrail_net = contrail_api_client.virtual_network_read(id=net['id'])
        set_network_policy(contrail_net, contrail_network_policy)

    # Check ping
    server_steps.check_ping_between_servers_via_floating(resources.servers)


def test_change_login_and_password(session, current_project,
                                   contrail_api_endpoint, create_user,
                                   user_steps, role_steps):
    """Verify that login and password can be changed.

    Steps:
        #. Create new user
        #. Make Contrail client with new user credentials
        #. Check that client is operable
        #. Change password for user
        #. Make Contrail client with new user credentials
        #. Check that client is operable
    """
    # Create user
    (user_name, ) = utils.generate_ids()
    password = user_name
    role = role_steps.get_role(name=stepler_config.ROLE_ADMIN)
    user = create_user(user_name=user_name, password=password)
    role_steps.grant_role(role, user, project=current_project)

    # Make Contrail client with new user credentials
    auth_params = {
        'type': 'keystone',
        'auth_url': session.auth.auth_url,
        'username': user_name,
        'password': password,
        'tenant_name': current_project.name
    }
    conn = client.Client(
        url=contrail_api_endpoint, auth_params=auth_params, blocking=False)

    # Check client operate
    assert_that(conn.virtual_networks_list(), is_not(empty()))

    # Change user password
    password = "password"
    user_steps.update_user(user, password=password)

    # Make Contrail client with new user credentials
    auth_params['password'] = password
    conn = client.Client(
        url=contrail_api_endpoint, auth_params=auth_params, blocking=False)

    # Check client operate
    net_list = waiter.wait(
        conn.virtual_networks_list,
        expected_exceptions=exceptions.AuthenticationFailed,
        timeout_seconds=settings.PASSWORD_CHANGE_TIMEOUT)
    assert_that(net_list, is_not(empty()))


def test_connectivity_from_server_without_floating(
        cirros_image, flavor, net_subnet_router, security_group, server_steps):
    """Check connectivity via external Contrail network without floating IP.

    Steps:
        #. Create network, subnet and router
        #. Launch new instance in created network
        #. Check ping from instance to external IP (8.8.8.8)
    """
    start, done = utils.generate_ids(count=2)
    userdata = '\n'.join([
        '#!/bin/sh',
        'echo {start}',
        'ping -w30 -c4 {ip}',
        'echo {done}',
    ]).format(
        ip=stepler_config.GOOGLE_DNS_IP, start=start, done=done)
    network, _, _ = net_subnet_router

    # Boot server
    server = server_steps.create_servers(
        image=cirros_image,
        flavor=flavor,
        networks=[network],
        security_groups=[security_group],
        userdata=userdata)[0]
    server_steps.check_server_log_contains_record(
        server, done, timeout=stepler_config.USERDATA_EXECUTING_TIMEOUT)

    # Check server console
    console = server.get_console_output()
    console = console.split(done)[0]
    console = console.split(start)[-1]
    console = console.strip()
    ping_result = ping.PingResult()
    ping_result.stdout = console
    assert_that(ping_result.loss, equal_to(0), console)
