# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import time

import attrdict
from hamcrest import assert_that, equal_to, greater_than  # noqa: H301
from pycontrail import types
import pytest
from stepler import config as stepler_config
from stepler.third_party import utils

from vapor import settings
from vapor.helpers import connectivity, policy, nodes_steps

try:
    import contextlib2 as contextlib
except ImportError:
    import contextlib


TCP_PORT = 7000
UDP_PORT = 7001


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
        # Add egress rule
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

    client, server = connectivity_test_resources.servers
    client_sg, server_sg = connectivity_test_resources.security_groups
    (client_floating_ip,
     server_floating_ip) = connectivity_test_resources.floating_ips
    client_sg_entries = client_sg.security_group_entries
    server_sg_entries = server_sg.security_group_entries

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
        # Add ingress rule
        server_sg_entries.add_policy_rule(
            policy.POLICY_RULE_ALLOW_INGRESS_ICMP)
        server_sg.security_group_entries = server_sg_entries
        contrail_api_client.security_group_update(server_sg)
        connectivity.check_icmp_connection_status(
            fixed_ip,
            server_ssh,
            timeout=settings.SECURITY_GROUP_APPLY_TIMEOUT)


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


@pytest.mark.parametrize(
    'contrail_2_servers_different_networks', [dict(ubuntu=True)],
    indirect=True,
    ids=['ubuntu'])
def test_add_remove_security_group_with_active_flow(
        contrail_2_servers_diff_nets_with_floating,
        neutron_security_group,
        contrail_api_client,
        contrail_network_policy,
        set_network_policy,
        os_faults_steps,
        port_steps,
        server_steps, ):
    """Add/remove SG from VM when flow is active and traffic from both ends.

    Steps:
        #. Create GS with allow all rules
        #. Create 2 networks
        #. Create 2 servers on different computes with created security group
        #. Generate iperf workload with TCP from server1 to server2
        #. Generate iperf workload with UDP from server2 to server1
        #. Check that TCP and UDP incoming traffics are present on both server1
            and server2
        #. Remove security group from server1
        #. Check that TCP and UDP incoming traffics are not present on both
            server1 and server2
        #. Add security group to server1
        #. Check that TCP and UDP incoming traffics are present on both server1
           and server2
    """
    # Update policy
    contrail_network_policy.network_policy_entries = (
        policy.ALLOW_ALL_POLICY_ENTRY)
    contrail_api_client.network_policy_update(contrail_network_policy)

    # Add policy to networks
    for network in contrail_2_servers_diff_nets_with_floating.networks:
        network = contrail_api_client.virtual_network_read(id=network['id'])
        set_network_policy(network, contrail_network_policy)

    # Add rule to group
    contrail_sg = contrail_api_client.security_group_read(
        id=neutron_security_group['id'])
    sg_entries = contrail_sg.security_group_entries
    rules = [
        types.PolicyRuleType(
            direction='>',
            protocol='any',
            action_list=types.ActionListType(simple_action='pass'),
            src_addresses=[
                types.AddressType(security_group=contrail_sg.get_fq_name_str())
            ],
            src_ports=[types.PortType()],
            dst_addresses=[types.AddressType(security_group='local')],
            dst_ports=[types.PortType()], ),
    ]
    sg_entries.policy_rule.extend(rules)
    contrail_sg.security_group_entries = sg_entries
    contrail_api_client.security_group_update(contrail_sg)
    server1, server2 = contrail_2_servers_diff_nets_with_floating.servers

    # Get ips, nodes, interfaces information
    ips = []
    computes = []
    ifaces = []
    for server in server1, server2:
        port = port_steps.get_port(
            device_owner=stepler_config.PORT_DEVICE_OWNER_SERVER,
            device_id=server.id)

        ips += [server_steps.get_fixed_ip(server)]

        node_name = getattr(server, settings.SERVER_ATTR_HYPERVISOR_HOSTNAME)
        node = os_faults_steps.get_node(fqdns=[node_name])
        computes.append(node)

        expected_name = 'tap{}'.format(port['id'])
        interfaces = nodes_steps.get_nodes_interfaces(os_faults_steps,
                                                      node)[node_name]
        iface = next(x for x in interfaces if expected_name.startswith(x))
        ifaces.append(iface)

        # install iperf
        with server_steps.get_server_ssh(server) as server_ssh:
            with server_ssh.sudo():
                server_ssh.check_call('apt-get install iperf -q -y')

    ip1, ip2 = ips

    udp_filter = "'(udp and src host {} and dst host {})'".format(ip1, ip2)
    tcp_filter = "'(tcp and src host {} and dst host {})'".format(ip2, ip1)

    with contextlib.ExitStack() as stack:
        enter = stack.enter_context
        server1_ssh = enter(server_steps.get_server_ssh(server1))
        server2_ssh = enter(server_steps.get_server_ssh(server2))

        # Start TCP and UDP traffic
        connectivity.start_iperf_pair(
            client_ssh=server2_ssh,
            server_ssh=server1_ssh,
            ip=ip1,
            port=TCP_PORT,
            timeout=60 * 1000)
        connectivity.start_iperf_pair(
            client_ssh=server1_ssh,
            server_ssh=server2_ssh,
            ip=ip2,
            port=UDP_PORT,
            udp=True,
            timeout=60 * 1000)

        # Check that some packets are captured
        connectivity.check_packets_on_iface(os_faults_steps, computes[0],
                                            ifaces[0], tcp_filter)
        connectivity.check_packets_on_iface(os_faults_steps, computes[1],
                                            ifaces[1], udp_filter)

        # Remove security group from server1
        server1.remove_security_group(neutron_security_group['id'])

        connectivity.check_packets_on_iface(
            os_faults_steps,
            computes[0],
            ifaces[0],
            tcp_filter,
            should_be=False)
        connectivity.check_packets_on_iface(
            os_faults_steps,
            computes[1],
            ifaces[1],
            udp_filter,
            should_be=False)

        # Add security group from server1
        server1.add_security_group(neutron_security_group['id'])

        time.sleep(10)

        connectivity.check_packets_on_iface(os_faults_steps, computes[0],
                                            ifaces[0], tcp_filter)
        connectivity.check_packets_on_iface(os_faults_steps, computes[1],
                                            ifaces[1], udp_filter)
