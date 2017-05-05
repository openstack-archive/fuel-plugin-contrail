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

from hamcrest import assert_that, all_of, contains_string, is_not
import pycontrail.types as types
from stepler import config as stepler_config


def _get_tcpdump_log_with_ping(server_steps, left_vm, right_vm, left_vm_fip,
                               right_vm_fip, right_vm_fixed_ip):
    """Start ping from left to right vm, returns right vm tcpdump's log."""
    log_file = '/tmp/tcpdump'
    with server_steps.get_server_ssh(
            right_vm, right_vm_fip['floating_ip_address']) as right_ssh:
        with right_ssh.sudo():
            right_ssh.check_call('apt-get install -y tcpdump')
            with server_steps.get_server_ssh(
                    left_vm, left_vm_fip['floating_ip_address']) as left_ssh:
                with server_steps.check_ping_loss_context(
                        right_vm_fixed_ip, server_ssh=left_ssh):
                    tcpdump_pid = right_ssh.background_call(
                        'tcpdump -i eth0 icmp', stdout=log_file)
                    time.sleep(10)
                    right_ssh.check_call('kill {}'.format(tcpdump_pid))
            return right_ssh.check_call('cat {}'.format(log_file)).stdout


def test_nat_service_instance(flavor, ubuntu_image, keypair, public_network,
                              neutron_security_group, contrail_2_networks,
                              create_floating_ip, contrail_network_policy,
                              set_network_policy, contrail_api_client,
                              server_steps, port_steps, service_instance):
    """Test contrail NAT service chain.

    Steps:
        #. Create flavor
        #. Create ubuntu image
        #. Create keypair
        #. Create security group
        #. Create left and right networks with subnets
        #. Create service template
        #. Create service instance with NAT service
        #. Create policy
        #. Assign policy to networks
        #. Create left and right vm on corresponding networks
        #. Start ping from left to right vm
        #. Check that left vm ip is present on tcpdump output on right vm
        #. Stop ping
        #. Add service instance to policy rule
        #. Start ping from left to right vm
        #. Check that left vm ip is absent on tcpdump output on right vm and
            right interface ip of service instance is present on tcpdump output
        #. Stop ping
    """
    # Add security group to NAT instance
    nat_vm_id = service_instance.get_virtual_machine_back_refs()[0]['uuid']
    nova_nat_instance = next(server for server in server_steps.get_servers()
                             if server.id == nat_vm_id)
    nova_nat_instance.add_security_group(neutron_security_group['id'])

    left_vn, right_vn = [
        contrail_api_client.virtual_network_read(id=net['id'])
        for net in contrail_2_networks.networks
    ]

    # Create policy rule with service
    rule = types.PolicyRuleType(
        action_list=types.ActionListType(simple_action='pass'),
        direction='<>',
        protocol='any',
        src_addresses=[
            types.AddressType(virtual_network=left_vn.get_fq_name_str())
        ],
        src_ports=[types.PortType()],
        dst_addresses=[
            types.AddressType(virtual_network=right_vn.get_fq_name_str())
        ],
        dst_ports=[types.PortType()])
    contrail_network_policy.set_network_policy_entries(
        types.PolicyEntriesType(policy_rule=[rule]))
    contrail_api_client.network_policy_update(contrail_network_policy)

    # Assign policy to networks
    set_network_policy(left_vn, contrail_network_policy)
    set_network_policy(right_vn, contrail_network_policy)

    # Create 2 servers
    servers = []
    floating_ips = []
    for net in contrail_2_networks.networks:
        server = server_steps.create_servers(
            flavor=flavor,
            image=ubuntu_image,
            networks=[net],
            security_groups=[neutron_security_group],
            keypair=keypair,
            username=stepler_config.UBUNTU_USERNAME)[0]

        servers.append(server)

        server_port = port_steps.get_port(
            device_owner=stepler_config.PORT_DEVICE_OWNER_SERVER,
            device_id=server.id)
        floating_ip = create_floating_ip(public_network, port=server_port)

        floating_ips.append(floating_ip)

    left_vm, right_vm = servers
    left_vm_fip, right_vm_fip = floating_ips

    # Install tcpdump on right vm
    with server_steps.get_server_ssh(
            right_vm, right_vm_fip['floating_ip_address']) as right_ssh:
        with right_ssh.sudo():
            right_ssh.check_call('apt-get install -y tcpdump')

    right_vm_fixed_ip = server_steps.get_fixed_ip(right_vm)
    nat_right_ip = nova_nat_instance.addresses[right_vn.name][0]['addr']
    left_vm_fixed_ip = server_steps.get_fixed_ip(left_vm)

    # Start ping from left to right server and tcpdump on right server
    tcpdump_stdout = _get_tcpdump_log_with_ping(
        server_steps, left_vm, right_vm, left_vm_fip, right_vm_fip,
        right_vm_fixed_ip)

    # Check that ICMP packets contains left vm ip address
    assert_that(tcpdump_stdout, contains_string(left_vm_fixed_ip))

    # Update policy rule
    rule.action_list.apply_service = [service_instance.get_fq_name_str()]
    contrail_network_policy.set_network_policy_entries(
        types.PolicyEntriesType(policy_rule=[rule]))
    contrail_api_client.network_policy_update(contrail_network_policy)

    # Start ping from left to right server and tcpdump on right server
    tcpdump_stdout = _get_tcpdump_log_with_ping(
        server_steps, left_vm, right_vm, left_vm_fip, right_vm_fip,
        right_vm_fixed_ip)

    # Check that ICMP packets has NAT right ip address and no contains left
    # vm ip address
    assert_that(tcpdump_stdout,
                all_of(
                    contains_string(nat_right_ip),
                    is_not(contains_string(left_vm_fixed_ip))))
