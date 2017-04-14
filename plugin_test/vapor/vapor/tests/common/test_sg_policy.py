# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import functools

import attrdict
import pytest
from stepler import config as stepler_config
from stepler.third_party import utils

from vapor.helpers import policy
from vapor.helpers import connectivity
from vapor import settings

SG_RULES = {
    'tcp_all': [{
        'direction': stepler_config.INGRESS,
        'protocol': 'tcp',
        'port_range_min': 1,
        'port_range_max': 65535,
        'remote_ip_prefix': '0.0.0.0/0',
    }],
    'tcp_ssh': [{
        'direction': stepler_config.INGRESS,
        'protocol': 'tcp',
        'port_range_min': 22,
        'port_range_max': 22,
        'remote_ip_prefix': '0.0.0.0/0',
    }],
    'udp_all': [{
        'direction': stepler_config.INGRESS,
        'protocol': 'udp',
        'port_range_min': 1,
        'port_range_max': 65535,
        'remote_ip_prefix': '0.0.0.0/0',
    }],
    'icmp_all': [{
        'direction': stepler_config.INGRESS,
        'protocol': 'icmp',
        'port_range_min': None,
        'port_range_max': None,
        'remote_ip_prefix': '0.0.0.0/0',
    }]
}

TCP_PORT = 7000
TCP_SSH_PORT = 22
UDP_PORT = 7001

check_tcp = functools.partial(
    connectivity.check_connection_status, port=TCP_PORT)
check_tcp_ssh = functools.partial(
    connectivity.check_connection_status, port=TCP_SSH_PORT, answer='SSH')
check_udp = functools.partial(
    connectivity.check_connection_status, port=UDP_PORT, udp=True)
check_icmp = connectivity.check_icmp_connection_status

tcp_all_policy = policy.make_policy_entry(
    protocol='tcp', src_ports_range=(-1, -1), dst_ports_range=(-1, -1))
tcp_ssh_policy = policy.make_policy_entry(
    protocol='tcp', src_ports_range=(-1, -1), dst_ports_range=(22, 22))


@pytest.fixture
def security_group(neutron_create_security_group,
                   neutron_security_group_rule_steps):
    """Fixture that returns security group with SSH allow rules."""
    group_name = next(utils.generate_ids('security-group'))
    group = neutron_create_security_group(group_name)

    neutron_security_group_rule_steps.add_rules_to_group(group['id'],
                                                         SG_RULES['tcp_ssh'])

    return group


@pytest.fixture
def connectivity_test_resources(
        cirros_image,
        flavor,
        security_group,
        public_network,
        contrail_network_policy,
        contrail_api_client,
        create_network,
        create_subnet,
        create_floating_ip,
        set_network_policy,
        server_steps,
        port_steps,
        floating_ip_steps, ):
    """Fixture for create 2 networks, boot 2 servers with network listeners.

    It returns attrdict with client and server instances, and server's
    listening ports.
    """
    servers = []
    floating_ips = []
    for i, name in enumerate(utils.generate_ids(count=2)):
        # Create network, subnet
        network = create_network(name)
        create_subnet(name, network=network, cidr='10.0.{}.0/24'.format(i))
        contrail_net = contrail_api_client.virtual_network_read(
            id=network['id'])
        set_network_policy(contrail_net, contrail_network_policy)

        # Boot server
        server = server_steps.create_servers(
            image=cirros_image,
            flavor=flavor,
            networks=[network],
            security_groups=[security_group],
            username=stepler_config.CIRROS_USERNAME,
            password=stepler_config.CIRROS_PASSWORD)[0]
        servers.append(server)

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

    server, client = servers

    # Start listeners
    with server_steps.get_server_ssh(server) as server_ssh:
        connectivity.start_port_listener(server_ssh, TCP_PORT)
        connectivity.start_port_listener(server_ssh, UDP_PORT, udp=True)

    # Detach 1st server floating IP
    floating_ip_steps.detach_floating_ip(floating_ips[0])
    return attrdict.AttrDict(server=server, client=client)


@pytest.mark.parametrize(
    ['sg_rules', 'checks'], [
        ([], {
            check_tcp: False,
            check_tcp_ssh: True,
            check_udp: False,
            check_icmp: False
        }),
        (SG_RULES['tcp_all'], {
            check_tcp: True,
            check_tcp_ssh: True,
            check_udp: False,
            check_icmp: False
        }),
        (SG_RULES['tcp_all'] + SG_RULES['udp_all'], {
            check_tcp: True,
            check_tcp_ssh: True,
            check_udp: True,
            check_icmp: False
        }),
    ],
    ids=['tcp_ssh', 'tcp_all', 'tcp_udp_all'])
def test_security_group_and_allow_all_policy(
        security_group, connectivity_test_resources, contrail_network_policy,
        neutron_security_group_rule_steps, server_steps, contrail_api_client,
        sg_rules, checks):
    """Verify traffic restrictions by security group with policy.

    Steps:
        #. Create network policy and allow all traffic
        #. Create security group and allow `sg_rules` traffic only
        #. Create 2 networks with policy
        #. Boot 2 servers with created security group, each - in its own
            network
        #. Add floating IP to one of server
        #. Check that security group rules are works as expected
    """

    # Update policy
    contrail_network_policy.network_policy_entries = (
        policy.ALLOW_ALL_POLICY_ENTRY)
    contrail_api_client.network_policy_update(contrail_network_policy)

    # Update security group
    neutron_security_group_rule_steps.add_rules_to_group(security_group['id'],
                                                         sg_rules)

    server1_ip = server_steps.get_fixed_ip(connectivity_test_resources.server)

    with server_steps.get_server_ssh(
            connectivity_test_resources.client) as server_ssh:
        for check, available in checks.items():
            check(
                ip=server1_ip,
                remote=server_ssh,
                must_available=available,
                timeout=60)


@pytest.mark.parametrize(
    ['policy_entries', 'checks'], [
        (tcp_all_policy, {
            check_tcp: True,
            check_tcp_ssh: True,
            check_udp: False,
            check_icmp: False
        }),
        (tcp_ssh_policy, {
            check_tcp: False,
            check_tcp_ssh: True,
            check_udp: False,
            check_icmp: False
        }),
    ],
    ids=['tcp_all', 'tcp_port'])
def test_allow_all_security_group_and_policies(
        contrail_network_policy, security_group,
        neutron_security_group_rule_steps, server_steps,
        connectivity_test_resources, contrail_api_client, policy_entries,
        checks):
    """Verify traffic restrictions by policy with security group.

    Steps:
        #. Create network policy with `policy_entries`
        #. Create security group and allow all traffic
        #. Create 2 networks with policy
        #. Boot 2 servers with created security group, each - in its own
            network
        #. Add floating IP to one of server
        #. Check that policy rules are works as expected
    """
    # Update policy
    contrail_network_policy.network_policy_entries = policy_entries
    contrail_api_client.network_policy_update(contrail_network_policy)

    # Update security group
    neutron_security_group_rule_steps.add_rules_to_group(
        security_group['id'],
        SG_RULES['tcp_all'] + SG_RULES['udp_all'] + SG_RULES['icmp_all'])

    server1_ip = server_steps.get_fixed_ip(connectivity_test_resources.server)

    with server_steps.get_server_ssh(
            connectivity_test_resources.client) as server_ssh:
        for check, available in checks.items():
            check(
                ip=server1_ip,
                remote=server_ssh,
                must_available=available,
                timeout=60)
