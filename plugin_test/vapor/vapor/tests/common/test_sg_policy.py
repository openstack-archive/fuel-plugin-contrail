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

from hamcrest import assert_that, equal_to  # noqa H301
import pytest
from stepler import config as stepler_config
from stepler.third_party import ping
from stepler.third_party import utils
from stepler.third_party import waiter

from vapor.helpers import policy
from vapor.helpers import connectivity

SG_RULES = {
    'tcp_all': [{
        'ip_protocol': 'tcp',
        'from_port': 1,
        'to_port': 65535,
        'cidr': '0.0.0.0/0',
    }],
    'tcp_ssh': [{
        'ip_protocol': 'tcp',
        'from_port': 22,
        'to_port': 22,
        'cidr': '0.0.0.0/0',
    }],
    'udp_all': [{
        'ip_protocol': 'udp',
        'from_port': 1,
        'to_port': 65535,
        'cidr': '0.0.0.0/0',
    }],
    'icmp_all': [{
        'ip_protocol': 'icmp',
        'from_port': -1,
        'to_port': -1,
        'cidr': '0.0.0.0/0',
    }]
}

TCP_PORT = 7000
TCP_SSH_PORT = 22
UDP_PORT = 7001

check_tcp = functools.partial(
    connectivity.check_connection_status, port=TCP_PORT)
check_tcp_ssh = functools.partial(
    connectivity.check_connection_status, port=TCP_SSH_PORT)
check_udp = functools.partial(
    connectivity.check_connection_status, port=UDP_PORT)


def check_icmp(ip, remote, must_available=True, timeout=0):
    def predicate():
        ping_result = ping.Pinger(ip, remote=remote).ping()
        if must_available:
            value = ping_result.loss
        else:
            value = ping_result.received
        return waiter.expect_that(value, equal_to(0))

    return waiter.wait(predicate, timeout_seconds=timeout)


@pytest.mark.parametrize(
    ['sg_rules', 'checks'], [
        (SG_RULES['tcp_all'], {
            check_tcp: True,
            check_tcp_ssh: True,
            check_udp: False,
            check_icmp: False
        }),
        (SG_RULES['tcp_ssh'], {
            check_tcp: False,
            check_tcp_ssh: True,
            check_udp: False,
            check_icmp: False
        }),
        (SG_RULES['tcp_all'] + SG_RULES['udp_all'], {
            check_tcp: True,
            check_tcp_ssh: True,
            check_udp: False,
            check_icmp: False
        }),
    ],
    ids=['tcp_all', 'tcp_ssh', 'tcp_udp_all'])
def test_security_group_and_allow_all_policy(
        contrail_network_policy, create_security_group, security_group_steps,
        floating_ip_steps, flavor, cirros_image, public_network,
        create_floating_ip, server_steps, port_steps, contrail_api_client,
        create_network, create_subnet, set_network_policy, sg_rules, checks):
    """Verify that policy that allows all are override security group.

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
        policy.allow_all_policy_entry)
    contrail_api_client.network_policy_update(contrail_network_policy)

    # Create security group
    security_group = create_security_group(next(utils.generate_ids()))
    security_group_steps.add_group_rules(security_group, sg_rules)

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
        floating_ips.append(floating_ip)

    # Start listeners
    tcp_server_cmd = 'nc -v -l -p {0} -e echo Reply'.format(TCP_PORT)
    udp_server_cmd = 'nc -v -u -l -p {0} -e echo Reply'.format(UDP_PORT)

    with server_steps.get_server_ssh(servers[0]) as server_ssh:
        server_ssh.background_call(tcp_server_cmd)
        server_ssh.background_call(udp_server_cmd)

    # Detach 1st server floating IP
    floating_ip_steps.detach_floating_ip(floating_ips[0])

    server1_ip = server_steps.get_fixed_ip(servers[0])

    with server_steps.get_server_ssh(servers[1]) as server_ssh:
        for check, available in checks.items():
            check(
                ip=server1_ip,
                remote=server_ssh,
                must_available=available,
                timeout=60)
