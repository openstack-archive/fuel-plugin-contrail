# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from six import moves
from stepler import config as stepler_config

from vapor import settings


def test_loadbalancer_after_deleting_server(
        flavor, cirros_image, net_subnet_router, security_group, loadbalancer,
        create_floating_ip, port_steps, server_steps, lb_listener, lb_pool,
        neutron_security_group_rule_steps, lbaas_steps):
    """Check loadbalancer after deleting server.

    Steps:
        #. Create network, subnet
        #. Create loadbalancer
        #. Create lbaas listener
        #. Create lbaas pool
        #. Create security group with allow ping rule
        #. Create floating IP on loadbalancer port
        #. Create 2 servers with simple HTTP server
        #. Add servers' IPs to loadbalancer pool
        #. Check that loadbalancer routes HTTP queries between servers
        #. Delete one of servers
        #. Check that loadbalancer pass all HTTP queries to single alive server
    """
    port = 80
    neutron_security_group_rule_steps.add_rule_to_group(
        security_group['id'],
        direction='ingress',
        protocol='tcp',
        port_range_min=port,
        port_range_max=port)

    http_server_cmd = settings.HTTP_SERVER_CMD.format(port=port)

    userdata = "\n".join([
        '#!/bin/sh -v',
        'screen -dmS daemon /bin/sh -c {cmd}',
        'screen -ls',
        'echo {done_marker}',
    ]).format(
        cmd=moves.shlex_quote(http_server_cmd),
        done_marker=stepler_config.USERDATA_DONE_MARKER)
    network, subnet, _ = net_subnet_router
    servers = server_steps.create_servers(
        count=2,
        image=cirros_image,
        flavor=flavor,
        networks=[network],
        security_groups=[security_group],
        userdata=userdata)
    for server in servers:
        server_steps.check_server_log_contains_record(
            server,
            stepler_config.USERDATA_DONE_MARKER,
            timeout=stepler_config.USERDATA_EXECUTING_TIMEOUT)

        ip = server_steps.get_fixed_ip(server)
        lbaas_steps.create_member(lb_pool, ip, port, subnet)

    vip_port = {'id': loadbalancer['vip_port_id']}
    port_steps.update(vip_port, security_groups=[security_group['id']])
    floating_ip = create_floating_ip(port=vip_port)

    lbaas_steps.check_balancing(
        floating_ip['floating_ip_address'], port, expected_count=2)

    server_steps.delete_servers(servers[1:])

    lbaas_steps.check_balancing(
        floating_ip['floating_ip_address'], port, expected_count=1)
