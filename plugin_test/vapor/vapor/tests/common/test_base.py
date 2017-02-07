# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import sys
from ipaddress import ip_address, ip_network
from hamcrest import (assert_that, calling, raises, contains_string, has_item,
                      has_entry, is_not, empty, equal_to, all_of)  # noqa H301
from neutronclient.common import exceptions as neutron_exceptions
from novaclient import exceptions as nova_exceptions
from stepler import config as stepler_config
from stepler.third_party import utils
from pycontrail import exceptions
import pycontrail.types as contrail_types
import pytest

from vapor.helpers import agent_steps
from vapor.helpers import asserts
from vapor.helpers import contrail_status, policy, connectivity
from vapor import settings
from vapor.helpers import contrail_status, nodes_steps


def test_network_deleting_with_server(network, server, contrail_api_client):
    assert_that(
        calling(contrail_api_client.virtual_network_delete).with_args(
            id=network['id']),
        raises(exceptions.RefsExistError))


def test_create_vm_bulk(net_subnet_router, tiny_flavor,
                        cirros_image, server_steps):
    """Description: Test to validate creation and deletion of VMs in bulk.
    Test steps:
        1. Create VMs in bulk, based on the count specified.
        2. Verify the VMs so created and cleanup of the VMs
           should also go through fine.
    Pass criteria:
        The creation and deletion of the VMs in bulk should go through fine.
    """
    network, _, _ = net_subnet_router
    BULK_SERVER_COUNT = 10
    servers = server_steps.create_servers(count=BULK_SERVER_COUNT,
                                          image=cirros_image,
                                          flavor=tiny_flavor,
                                          networks=[network])
    server_steps.delete_servers(servers)


def test_delete_vm_with_associated_vn(contrail_network, contrail_subnet,
                                      tiny_flavor, cirros_image,
                                      server_steps, network_steps,
                                      contrail_api_client):
    """Description: Test to validate that VN cannot be deleted if
        there is a VM associated with it.
    Test steps:
        1. Create a VN and launch a VM in that VN.
        2. Verify that with the VM still existing,
           it is not possible to delete the VN.
    Pass criteria:
        The attempt to delete VN should fail.
    """
    server_steps.create_servers(
        image=cirros_image, flavor=tiny_flavor,
        nics=[{'net-id': contrail_network.uuid}])
    net = network_steps.get_network(id=contrail_network.uuid)

    # Check that we can't delete this net.
    assert_that(calling(network_steps.delete).with_args(net),
                raises(neutron_exceptions.NetworkInUseClient))

    # Check that network is still there
    # via contrail API
    c_networks = contrail_api_client.virtual_networks_list()
    assert_that(c_networks['virtual-networks'],
                has_item(has_entry('uuid', contrail_network.uuid)))

    # via neutron API
    assert_that(network_steps.get_network_by_name(net['name']),
                is_not(empty()))


def test_two_nets_same_name(contrail_api_client, contrail_network,
                            contrail_subnet):
    """Description: Test to validate that with the same subnet and
        name provided, two different VNs cannot be created.
    Test steps:
        1. Create a VN.
        2. Create a second VN with the same name and subnet as the first VN.
        3. Verify that no second VN object is created.
    Pass criteria:
        There is a single VN created.
    """
    net = contrail_types.VirtualNetwork(contrail_network.name)
    assert_that(
        calling(contrail_api_client.virtual_network_create).with_args(net),
        raises(exceptions.RefsExistError))


def test_metadata_service(security_group, port_steps,
                          network, subnet, public_network, flavor,
                          create_floating_ip, tiny_flavor, cirros_image,
                          server_steps):
    """Description: Test to validate metadata service
    Test steps:
        1. Create a VN.
        2. Launch a VM in this VN.
        3. Write a metadata script to print the current time.
        4. Pass this during the VM launch.
    Pass criteria:
        The output of the metadata script should be seen in the VM.
    """
    output_filename = 'output.txt'
    userdata = (
        u'#!/bin/sh\n'
        u'echo "TestMetadataService.'
        u'The time is now $(date -R)!" | tee /tmp/{filename}\n'.format(
            filename=output_filename
        )
    )

    server, = server_steps.create_servers(
        image=cirros_image,
        flavor=flavor,
        networks=[network],
        security_groups=[security_group],
        userdata=userdata,
        username=stepler_config.CIRROS_USERNAME,
        password=stepler_config.CIRROS_PASSWORD)

    server1_port = port_steps.get_port(
        device_owner=stepler_config.PORT_DEVICE_OWNER_SERVER,
        device_id=server.id)
    floating_ip = create_floating_ip(public_network, port=server1_port)

    with server_steps.get_server_ssh(server,
                                     ip=floating_ip['floating_ip_address'],
                                     ssh_timeout=60) as server_ssh:
        res = server_ssh.execute(u'ls /tmp/', timeout=60)
        assert_that(res.stdout, contains_string(output_filename))


def test_restart_control_service(os_faults_steps):
    """Validate restart of control node services."""
    control_nodes_fqdns = settings.CONTRAIL_ROLES_DISTRIBUTION[
        settings.ROLE_CONTRAIL_CONTROLLER]
    control_nodes = os_faults_steps.get_nodes(fqdns=control_nodes_fqdns)

    contrail_status.check_service_status(
        os_faults_steps,
        control_nodes_fqdns,
        'contrail-control',
        'active',
        timeout=0)
    # Stop services
    os_faults_steps.execute_cmd(control_nodes, 'service contrail-control stop')
    contrail_status.check_service_status(
        os_faults_steps,
        control_nodes_fqdns,
        'contrail-control',
        'inactive',
        timeout=settings.SERVICE_STATUS_CHANGE_TIMEOUT)
    # Start services
    os_faults_steps.execute_cmd(control_nodes,
                                'service contrail-control start')
    contrail_status.check_service_status(
        os_faults_steps,
        control_nodes_fqdns,
        'contrail-control',
        'active',
        timeout=settings.SERVICE_STATUS_CHANGE_TIMEOUT)


@pytest.mark.usefixtures('contrail_network_cleanup')
def test_vn_name_with_special_characters(contrail_api_client,
                                         contrail_current_project):
    """Validate creating virtual network with special characters in name.

    Steps:
        #. Create VN with special characters in name
        #. Check that VN created successfully and is present in networks list
    """
    network_name, = utils.generate_ids(use_unicode=True)
    net = contrail_types.VirtualNetwork(
        network_name, parent_obj=contrail_current_project)
    contrail_api_client.virtual_network_create(net)
    networks = contrail_api_client.virtual_networks_list()
    assert_that(networks['virtual-networks'],
                has_item(has_entry('uuid', net.uuid)))


def test_create_server_on_exhausted_subnet(cirros_image, flavor, network,
                                           create_subnet, create_port,
                                           server_steps):
    """Validate that a VMs cannot be created after the IP-Block is exhausted.

    Steps:
        #. Create network
        #. Create subnet with CIDR 10.0.0.0/28
        #. Create server in network
        #. Check that server reaches active status
        #. Create as many ports on network as possible
        #. Create another server in network
        #. Check that second server reaches error status
    """
    name, = utils.generate_ids()
    create_subnet(name, network, cidr='10.0.0.0/28')
    create_server_args = dict(
        image=cirros_image, flavor=flavor, networks=[network])
    server_steps.create_servers(**create_server_args)
    while True:
        try:
            create_port(network)
        except neutron_exceptions.BadRequest:
            if 'exhausted' in str(sys.exc_value):
                break
            else:
                raise

    assert_that(
        calling(server_steps.create_servers).with_args(**create_server_args),
        raises(AssertionError, 'No valid host was found'))


def test_file_transfer_with_scp(
        ubuntu_image, keypair, flavor, create_floating_ip, public_network,
        network, subnet, security_group, server_steps, port_steps):
    """Validate File Transfer using scp between VMs.

    Steps:
        #. Create network
        #. Create 2 servers
        #. Create file on server1
        #. Transfer file to server2 with scp
        #. Verify transferred file size
        #. Repeat transfer for next file sizes:
            1000,1101,1202,1303,1373, 1374,2210, 2845, 3000, 10000, 10000003
    """
    sizes = [
        1000, 1101, 1202, 1303, 1373, 1374, 2210, 2845, 3000, 10000, 10000003
    ]
    username = stepler_config.UBUNTU_USERNAME
    path = '/home/{}/file'.format(username)
    key_content = keypair.private_key
    key_path = '/home/{}/key'.format(username)
    userdata = '\n'.join([
        "#!/bin/bash -v",
        "echo '{content}' > {path}",
        "chown {user} {path}",
        "chmod 600 {path}",
    ]).format(
        content=key_content, path=key_path, user=username)

    ssh_opts = ('-o UserKnownHostsFile=/dev/null '
                '-o StrictHostKeyChecking=no')

    # Boot servers
    servers = server_steps.create_servers(
        count=2,
        image=ubuntu_image,
        flavor=flavor,
        networks=[network],
        security_groups=[security_group],
        keypair=keypair,
        userdata=userdata,
        username=username)

    # Assign floating ips
    floating_ips = []
    for server in servers:
        port = port_steps.get_port(
            device_owner=stepler_config.PORT_DEVICE_OWNER_SERVER,
            device_id=server.id)
        floating_ip = create_floating_ip(public_network, port=port)
        floating_ips.append(floating_ip)

    ip = server_steps.get_fixed_ip(servers[1])
    with asserts.AssertsCollector() as collector:
        for size in sizes:
            # Transfer file
            with server_steps.get_server_ssh(
                    servers[0],
                    floating_ips[0]['floating_ip_address']) as server1_ssh:
                server1_ssh.check_call(
                    'fallocate -l {size} {path}'.format(size=size, path=path))
                server1_ssh.check_call(
                    'scp -i {key} {ssh_opts} {path} {user}@{ip}:{path}'.format(
                        key=key_path,
                        path=path,
                        user=username,
                        ip=ip,
                        ssh_opts=ssh_opts))

            # Check file size
            with server_steps.get_server_ssh(
                    servers[1],
                    floating_ips[1]['floating_ip_address']) as server2_ssh:
                actual_size = server2_ssh.check_call(
                    'stat -c %s {}'.format(path)).stdout
                collector.check(actual_size, equal_to(str(size)))


def test_various_type_of_subnets_associated_with_vn(
        cirros_image,
        flavor,
        security_group,
        contrail_network,
        contrail_current_project,
        contrail_create_subnet,
        create_virtual_interface,
        contrail_create_instance_ip,
        server_steps,
        create_floating_ip,
        public_network):
    """Validate that 2 subnets with different CIDR on single VN works.

    Steps:
        #. Create network
        #. Create subnet_1
        #. Create subnet 2 with different CIDR
        #. Create 2 ports on VN for each subnet
        #. Boot nova server with created ports
        #. Execute `sudo cirros-dhcpd up <iface>` for all interfaces on server
        #. Check that server gets correct IP addresses on all interfaces
    """
    ip1 = '10.0.0.10'
    ip2 = '10.10.0.10'
    iface_names = ('eth0', 'eth1')
    contrail_create_subnet(
        contrail_network, ip_prefix='10.0.0.0', ip_prefix_len=24)
    contrail_create_subnet(
        contrail_network, ip_prefix='10.10.0.0', ip_prefix_len=16)

    iface1 = create_virtual_interface(contrail_network)
    iface2 = create_virtual_interface(contrail_network)

    ip1 = contrail_create_instance_ip(contrail_network, iface1, ip1)
    ip2 = contrail_create_instance_ip(contrail_network, iface2, ip2)
    server = server_steps.create_servers(
        image=cirros_image,
        flavor=flavor,
        nics=[{
            'port-id': iface1.uuid,
        }, {
            'port-id': iface2.uuid
        }],
        security_groups=[security_group],
        username=stepler_config.CIRROS_USERNAME,
        password=stepler_config.CIRROS_PASSWORD)[0]
    floating_ip = create_floating_ip(public_network, port={'id': iface1.uuid})
    with server_steps.get_server_ssh(
            server, floating_ip['floating_ip_address']) as server_ssh:
        with server_ssh.sudo():
            for name in iface_names:
                server_ssh.check_call('/sbin/cirros-dhcpc up {}'.format(name))
        result = server_ssh.check_call('ip a')
    assert_that(result.stdout,
                all_of(*[contains_string(name) for name in iface_names]))


def test_create_server_on_network_without_subnet(
        cirros_image,
        flavor,
        contrail_network,
        server_steps, ):
    """Creating server on network without subnet should raise an exception."""
    assert_that(
        calling(server_steps.create_servers).with_args(
            image=cirros_image,
            flavor=flavor,
            networks=[{
                'id': contrail_network.uuid
            }],
            check=False),
        raises(nova_exceptions.BadRequest, 'requires a subnet'))


def test_vm_multi_intf_in_same_vn_chk_ping(network,
                                           subnet,
                                           cirros_image,
                                           flavor,
                                           security_group,
                                           server_steps,
                                           port_steps,
                                           create_floating_ip,
                                           public_network):
    """Test to validate that a multiple interfaces of the same VM can be
    associated to the same VN and ping is successful.
    """
    userdata = (
        u'#!/bin/sh\n'
        u"/sbin/ifconfig -a\n"
        u"/sbin/cirros-dhcpc up eth1\n")

    server = server_steps.create_servers(
        userdata=userdata,
        image=cirros_image,
        flavor=flavor,
        security_groups=[security_group],
        networks=[network, network],
        username=stepler_config.CIRROS_USERNAME,
        password=stepler_config.CIRROS_PASSWORD)[0]

    server_ports = port_steps.get_ports(
        device_owner=stepler_config.PORT_DEVICE_OWNER_SERVER,
        device_id=server.id)

    server_port = server_ports[0]
    floating_ip = create_floating_ip(public_network, port=server_port)
    server_steps.check_server_ip(server,
                                 floating_ip['floating_ip_address'],
                                 timeout=settings.FLOATING_IP_BIND_TIMEOUT)

    server_steps.check_ping_between_servers_via_floating(
        [server, server],
        ip_types=(stepler_config.FIXED_IP,))


@pytest.mark.parametrize('flavor', [dict(ram=128, disk=1)], indirect=True)
def test_create_multiple_servers_on_many_networks(
        cirros_image, flavor, create_network, create_subnet, server_steps):
    """Validate creation of multiple VN with multiple subnet and VMs in it.

    Steps:
        #. Create 2 networks with subnets
        #. Create 4 servers on each of network
        #. Check that all servers reach ACTIVE state
    """
    networks = []
    for name in utils.generate_ids(count=2):
        network = create_network(name)
        networks.append(network)
        create_subnet(
            name + '__subnet', network=network, cidr=stepler_config.LOCAL_CIDR)

    for network in networks:
        server_steps.create_servers(
            count=4, flavor=flavor, image=cirros_image, networks=[network])


def test_network_in_agent_with_server_add_delete(
        contrail_api_client, session, contrail_services_http_introspect_ports,
        network, server, server_steps):
    """Validate network's existence and removal in agent.

    Steps:
        #. Create network, subnet
        #. Launch server on it
        #. Check that network is present on one of vrouter agent
        #. Delete server
        #. Check that network is not present on any of vrouter agent
    """
    contrail_network = contrail_api_client.virtual_network_read(
        id=network['id'])
    network_fq_name = contrail_network.get_fq_name_str()

    nodes = contrail_services_http_introspect_ports['contrail-vrouter-agent']
    port = nodes['port']
    agent_networks = []
    for ip in nodes['ips']:
        agent_network = agent_steps.get_vna_vn(session, ip, port,
                                               network_fq_name)
        if agent_network:
            agent_networks.append(agent_network)

    assert_that(agent_networks, is_not(empty()))

    server_steps.delete_servers([server])

    agent_networks = []
    for ip in nodes['ips']:
        agent_network = agent_steps.get_vna_vn(session, ip, port,
                                               network_fq_name)
        if agent_network:
            agent_networks.append(agent_network)

    assert_that(agent_networks, empty())


def test_policy_between_vns_diff_proj(different_tenants_resources,
                                      server_steps,
                                      contrail_api_client,
                                      create_contrail_security_group):
    """Test to validate that policy to deny and pass under different
    projects should behave accordingly.

    Test steps:
        1. Create 2 different projects.
        2. Launch 2 VNs and 2 VMs.
        3. Configure a policy to allow ICMP in one of the projects, while
        in the other configure a policy to deny ICMP between the projects.
    """
    project1, project2 = different_tenants_resources

    client, server = project1.server, project2.server
    client_floating_ip = project1.floating_ip
    server_floating_ip = project2.floating_ip

    prj1_conrail_sg = contrail_api_client.security_group_read(
        id=project1.security_group.id)
    prj2_conrail_sg = contrail_api_client.security_group_read(
        id=project2.security_group.id)

    client_sg_entries = prj1_conrail_sg.security_group_entries
    server_sg_entries = prj2_conrail_sg.security_group_entries

    # Add allow policy
    client_sg_entries.add_policy_rule(policy.POLICY_RULE_ALLOW_EGRESS_ICMP)
    client_sg_entries.add_policy_rule(policy.POLICY_RULE_ALLOW_INGRESS_ICMP)
    prj1_conrail_sg.security_group_entries = client_sg_entries
    contrail_api_client.security_group_update(prj1_conrail_sg)

    with server_steps.get_server_ssh(
            client,
            ip=client_floating_ip['floating_ip_address']) as server_ssh:
        connectivity.check_icmp_connection_status(
            server_floating_ip['floating_ip_address'],
            server_ssh,
            must_available=False,
            timeout=settings.SECURITY_GROUP_APPLY_TIMEOUT)

        server_sg_entries.add_policy_rule(policy.POLICY_RULE_ALLOW_EGRESS_ICMP)
        server_sg_entries.add_policy_rule(policy.POLICY_RULE_ALLOW_INGRESS_ICMP)
        prj2_conrail_sg.security_group_entries = server_sg_entries
        contrail_api_client.security_group_update(prj2_conrail_sg)

        connectivity.check_icmp_connection_status(
            server_floating_ip['floating_ip_address'],
            server_ssh,
            timeout=settings.SECURITY_GROUP_APPLY_TIMEOUT)


def test_vm_associated_2vn(cirros_image, flavor, security_group,
                           contrail_2_networks, server_steps):
    """Test to validate a VM associated with two VNs.
    Test steps:
        1. Create 2 VNs.
        2. Launch a VM such that it has address from both the VNs.
    Pass criteria:
        VM should get both the IPs.
    """
    server = server_steps.create_servers(
        image=cirros_image,
        flavor=flavor,
        networks=contrail_2_networks.networks,
        security_groups=[security_group])[0]
    server_ips = server_steps.get_ips(server)
    nets = {net['name'] for net in contrail_2_networks.networks}
    server_nets = {ip['net'] for addr, ip in server_ips.items()}
    server_ips = {ip_address(addr) for addr, ip in server_ips.items()}
    cidrs = {ip_network(subnet['cidr'])
             for subnet in contrail_2_networks.subnets}
    assert_that(nets, equal_to(server_nets))
    # Check each CIDR for each IP
    ips_in_cidr = {ip for ip in server_ips for cidr in cidrs if ip in cidr}
    assert_that(server_ips, equal_to(ips_in_cidr))


def test_update_vm_ip(server, subnet, port_steps, server_steps):
    """Test to validate that updating the IP address of the VM fails.
    Test steps:
        1. Create a VM in a VN.
        2. Try to update the IP of the VM.
    Pass criteria:
        Modification of fixed IP will not be allowed.
        Proper error should be observed.
    """
    server_fixed_ip = server_steps.get_fixed_ip(server)
    # Find new IP address from server's network
    server_fixed_ip_new = ''
    for net_ip in ip_network(subnet['cidr']).hosts():
        if str(net_ip) != server_fixed_ip:
            server_fixed_ip_new = str(net_ip)
            break

    server_port = port_steps.get_port(
        device_owner=stepler_config.PORT_DEVICE_OWNER_SERVER,
        device_id=server.id)
    port_dict = {
        'fixed_ips': [{'subnet_id': subnet['id'],
                       'ip_address': server_fixed_ip_new}]
    }
    assert_that(
        calling(port_steps.update).with_args(server_port,
                                             check=False,
                                             **port_dict),
        raises(neutron_exceptions.BadRequest))

