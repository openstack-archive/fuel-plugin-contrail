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
import itertools
from ipaddress import ip_address, ip_network
from hamcrest import (assert_that, calling, raises, contains_string, has_item,
                      has_entry, is_not, empty, equal_to)  # noqa H301
from neutronclient.common import exceptions as neutron_exceptions
from stepler import config as stepler_config
from stepler.third_party import utils
from pycontrail import exceptions
import pycontrail.types as contrail_types
import pytest

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
def test_vn_name_with_special_characters(contrail_api_client, contrail_current_project):
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


def test_vm_associated_2vn(server_steps,
                           cirros_image, flavor, security_group,
                           contrail_2_networks):
    """Test to validate a VM associated with two VNs.
    Test steps:
        1. Create 2 VNs.
        2. Launch a VM such that it has address from both the VNs.
    Pass criteria:
        VM should get both the IPs.
    """
    server = server_steps.create_servers(
        count=1,
        image=cirros_image,
        flavor=flavor,
        networks=contrail_2_networks.networks,
        security_groups=[security_group])[0]
    server_ips = server_steps.get_ips(server)
    nets = {net['name'] for net in contrail_2_networks.networks}
    ip_nets = {ip['net'] for addr, ip in server_ips.items()}
    ips = {ip_address(addr) for addr, ip in server_ips.items()}
    cidrs = {ip_network(port_info['cidr'])
             for port_info in contrail_2_networks.subnets}
    assert_that(nets, equal_to(ip_nets))
    # Check each CIDR for each IP
    checks = {ip for ip in ips for cidr in cidrs if ip in cidr}
    assert_that(ips, equal_to(checks))


def test_update_vm_ip(server_steps, security_group, create_network,
                      create_subnet, cirros_image, flavor, port_steps):
    """Test to validate that updating the IP address of the VM fails.
    Test steps:
        1. Create a VM in a VN.
        2. Try to update the IP of the VM.
    Pass criteria:
        Modification of fixed IP will not be allowed.
        Proper error should be observed.
    """
    name_net = next(utils.generate_ids(count=1))
    name_subnet = name_net + '__subnet'
    cidr = '10.0.0.0/24'
    fixed_ip = '10.0.0.5'
    fixed_ip_new = '10.0.0.10'
    network = create_network(name_net)
    subnet = create_subnet(name_subnet, network=network, cidr=cidr)
    server = server_steps.create_servers(image=cirros_image,
                                         flavor=flavor,
                                         nics=[{'net-id': network['id'],
                                                'v4-fixed-ip': fixed_ip}],
                                         security_groups=[security_group])[0]
    server_port = port_steps.get_port(
        device_owner=stepler_config.PORT_DEVICE_OWNER_SERVER,
        device_id=server.id)
    port_dict = {
        'fixed_ips': [{'subnet_id': subnet['id'], 'ip_address': fixed_ip_new}]
    }
    assert_that(
        calling(port_steps.update).with_args(server_port,
                                             check=False,
                                             **port_dict),
        raises(neutron_exceptions.BadRequest))

