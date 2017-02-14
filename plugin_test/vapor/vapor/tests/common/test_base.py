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

from hamcrest import (assert_that, calling, raises, contains_string, has_item,
                      has_entry, is_not, empty, all_of)  # noqa: H301
from neutronclient.common import exceptions as neutron_exceptions
from novaclient import exceptions as nova_exceptions
from stepler import config as stepler_config
from stepler.third_party import utils
from pycontrail import exceptions
import pycontrail.types as contrail_types
import pytest

from vapor.helpers import contrail_status
from vapor import settings


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
