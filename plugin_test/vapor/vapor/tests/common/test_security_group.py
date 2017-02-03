# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import attrdict
from hamcrest import assert_that, equal_to  # noqa: H301
import pytest
from stepler import config as stepler_config
from stepler.third_party import utils

from vapor.helpers import connectivity
from vapor.helpers import policy
from vapor import settings


@pytest.fixture
def connectivity_test_resources(
        public_network,
        cirros_image,
        flavor,
        network,
        subnet,
        create_contrail_security_group,
        create_floating_ip,
        contrail_api_client,
        server_steps,
        port_steps, ):
    """Fixture that creates network, 3 security groups and 2 servers.

    It returns attrdict with client and server instances, and server's
    listening ports.
    """
    # Create security groups
    security_groups = []
    for name in utils.generate_ids(count=3):
        group = create_contrail_security_group(name)
        security_groups.append(group)

    # Allow ingress SSH for one of groups
    ssh_sg = security_groups.pop()
    ssh_sg.security_group_entries.add_policy_rule(
        policy.POLICY_RULE_ALLOW_INGRESS_SSH)
    contrail_api_client.security_group_update(ssh_sg)

    # Boot servers
    servers = server_steps.create_servers(
        count=2,
        image=cirros_image,
        flavor=flavor,
        networks=[network],
        security_groups=[attrdict.AttrDict(id=ssh_sg.uuid)],
        username=stepler_config.CIRROS_USERNAME,
        password=stepler_config.CIRROS_PASSWORD)
    floating_ips = []
    for server in servers:
        # Assign floating IP
        port = port_steps.get_port(
            device_owner=stepler_config.PORT_DEVICE_OWNER_SERVER,
            device_id=server.id)
        floating_ip = create_floating_ip(public_network, port=port)
        server_steps.check_server_ip(
            server,
            floating_ip['floating_ip_address'],
            timeout=settings.FLOATING_IP_BIND_TIMEOUT)
        floating_ips.append(floating_ip)
    return attrdict.AttrDict(
        servers=servers,
        floating_ips=floating_ips,
        security_groups=security_groups)


def test_inbound_traffic_without_ingress_rule(
        connectivity_test_resources, server_steps, contrail_api_client,
        nova_client):
    """Verify that inbound traffic without ingress rule is blocked.

    Steps:
        #. Create security group for ingress SSH
        #. Create security group for server
        #. Create security group for client
        #. Create network with subnet
        #. Boot 2 nova instances (client and server) in network
        #. Add Floating IP to client
        #. Add security group to client with allow all rules
        #. Add security group to server with allow egress ICMP rule
        #. Check that there are no success pings from client to server
        #. Add ingress ICMP rule to server's security group
        #. Check that there are success pings from client to server
    """
    client, server = connectivity_test_resources.servers
    client_sg, server_sg = connectivity_test_resources.security_groups
    client_floating_ip = connectivity_test_resources.floating_ips[0]
    client_sg_entries = client_sg.security_group_entries
    server_sg_entries = server_sg.security_group_entries

    # Add security group to client and server
    nova_client.servers.add_security_group(client, client_sg.name)
    nova_client.servers.add_security_group(server, server_sg.name)

    # Setup client and server security groups
    client_sg_entries.add_policy_rule(policy.POLICY_RULE_ALLOW_EGRESS_ALL)
    client_sg_entries.add_policy_rule(policy.POLICY_RULE_ALLOW_INGRESS_ALL)
    client_sg.security_group_entries = client_sg_entries
    contrail_api_client.security_group_update(client_sg)

    server_sg_entries.add_policy_rule(policy.POLICY_RULE_ALLOW_EGRESS_ICMP)
    server_sg.security_group_entries = server_sg_entries
    contrail_api_client.security_group_update(server_sg)

    # Check icmp traffic before and after adding ingress rule to server's
    # security group
    fixed_ip = server_steps.get_fixed_ip(server)
    with server_steps.get_server_ssh(
            client,
            ip=client_floating_ip['floating_ip_address']) as server_ssh:
        connectivity.check_icmp_connection_status(
            fixed_ip,
            server_ssh,
            must_available=False,
            timeout=settings.SECURITY_GROUP_APPLY_TIMEOUT)
        # Add ingress rule
        server_sg_entries.add_policy_rule(
            policy.POLICY_RULE_ALLOW_INGRESS_ICMP)
        server_sg.security_group_entries = server_sg_entries
        contrail_api_client.security_group_update(server_sg)
        connectivity.check_icmp_connection_status(
            fixed_ip,
            server_ssh,
            timeout=settings.SECURITY_GROUP_APPLY_TIMEOUT)


def test_outbound_traffic_without_egress_rule(
        connectivity_test_resources, server_steps, contrail_api_client,
        nova_client):
    """Verify that outbound traffic without egress rule is blocked.

    Steps:
        #. Create security group for ingress SSH
        #. Create security group for server
        #. Create security group for client
        #. Create network with subnet
        #. Boot 2 nova instances (client and server) in network
        #. Add Floating IP to client
        #. Add security group to client with allow ingress ICMP rule
        #. Add security group to server with allow all rules
        #. Check that there are no success pings from client to server
        #. Add egress ICMP rule to client's security group
        #. Check that there are success pings from client to server
    """
    client, server = connectivity_test_resources.servers
    client_sg, server_sg = connectivity_test_resources.security_groups
    client_floating_ip = connectivity_test_resources.floating_ips[0]
    client_sg_entries = client_sg.security_group_entries
    server_sg_entries = server_sg.security_group_entries

    # Add security group to client and server
    nova_client.servers.add_security_group(client, client_sg.name)
    nova_client.servers.add_security_group(server, server_sg.name)

    # Setup client and server security groups
    server_sg_entries.add_policy_rule(policy.POLICY_RULE_ALLOW_EGRESS_ALL)
    server_sg_entries.add_policy_rule(policy.POLICY_RULE_ALLOW_INGRESS_ALL)
    server_sg.security_group_entries = server_sg_entries
    contrail_api_client.security_group_update(server_sg)

    client_sg_entries.add_policy_rule(policy.POLICY_RULE_ALLOW_INGRESS_ICMP)
    client_sg.security_group_entries = client_sg_entries
    contrail_api_client.security_group_update(client_sg)

    # Check icmp traffic before and after adding ingress rule to server's
    # security group
    fixed_ip = server_steps.get_fixed_ip(server)
    with server_steps.get_server_ssh(
            client,
            ip=client_floating_ip['floating_ip_address']) as server_ssh:
        connectivity.check_icmp_connection_status(
            fixed_ip,
            server_ssh,
            must_available=False,
            timeout=settings.SECURITY_GROUP_APPLY_TIMEOUT)
        # Add ingress rule
        client_sg_entries.add_policy_rule(policy.POLICY_RULE_ALLOW_EGRESS_ICMP)
        client_sg.security_group_entries = client_sg_entries
        contrail_api_client.security_group_update(client_sg)
        connectivity.check_icmp_connection_status(
            fixed_ip,
            server_ssh,
            timeout=settings.SECURITY_GROUP_APPLY_TIMEOUT)


def test_security_group_without_rules(connectivity_test_resources,
                                      server_steps, floating_ip_steps,
                                      contrail_api_client, nova_client):
    """Verify that security group without rules deny any traffic.

    Steps:
        #. Create 2 security groups
        #. Create network with subnet
        #. Boot 2 nova instances (client and server) in network
        #. Add Floating IP to client
        #. Add security group to client with allow all rules
        #. Add security group to server without rules
        #. Check that there are no success pings from client to server
        #. Add egress ICMP rule to client's security group
        #. Check that there are success pings from client to server
    """
    TCP_PORT = 7000
    UDP_PORT = 7001

    client, server = connectivity_test_resources.servers
    client_sg, server_sg = connectivity_test_resources.security_groups
    (client_floating_ip,
     server_floating_ip) = connectivity_test_resources.floating_ips
    client_sg_entries = client_sg.security_group_entries

    # Start server listeners
    with server_steps.get_server_ssh(
            server, server_floating_ip['floating_ip_address']) as server_ssh:
        connectivity.start_port_listener(server_ssh, TCP_PORT)
        connectivity.start_port_listener(server_ssh, UDP_PORT, udp=True)

    # Remove server floating ip
    floating_ip_steps.detach_floating_ip(server_floating_ip)

    # Setup client and server security groups
    server_sg.security_group_entries = None
    contrail_api_client.security_group_update(server_sg)

    client_sg_entries.add_policy_rule(policy.POLICY_RULE_ALLOW_EGRESS_ALL)
    client_sg_entries.add_policy_rule(policy.POLICY_RULE_ALLOW_INGRESS_ALL)
    client_sg.security_group_entries = client_sg_entries
    contrail_api_client.security_group_update(client_sg)

    # Add security group to client
    nova_client.servers.add_security_group(client, client_sg.name)

    # Remove all and add clear security group server
    for security_group in server.security_groups:
        nova_client.servers.remove_security_group(server,
                                                  security_group['name'])
    nova_client.servers.add_security_group(server, server_sg.name)

    fixed_ip = server_steps.get_fixed_ip(server)
    with server_steps.get_server_ssh(
            client,
            ip=client_floating_ip['floating_ip_address']) as server_ssh:
        # Check no icmp traffic
        connectivity.check_icmp_connection_status(
            fixed_ip, server_ssh, must_available=False)
        # Check no tcp traffic
        connectivity.check_connection_status(
            fixed_ip, server_ssh, port=TCP_PORT, must_available=False)
        # Check no udp traffic
        connectivity.check_connection_status(
            fixed_ip,
            server_ssh,
            port=UDP_PORT,
            udp=True,
            must_available=False)


def test_security_group_rules_uuid_in_contrail_and_neutron(contrail_api_client,
                                                           neutron_client):
    """Check that neutron and contrail has same uuid for SG rules.

    Steps:
        #. Retrieve all SG rules with neutron API
        #. Retrieve all SG rules with contrail API
        #. Check that uuids' sets are equals
    """
    neutron_rules = neutron_client.security_group_rules.list()
    neutron_rules_uuids = {x['id'] for x in neutron_rules}
    contrail_rules_uuids = set()
    for group in contrail_api_client.security_groups_list(detail=True):
        for rule in group.security_group_entries.policy_rule:
            contrail_rules_uuids.add(rule.rule_uuid)
    assert_that(contrail_rules_uuids, equal_to(neutron_rules_uuids))
