# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from hamcrest import (assert_that, calling, raises, contains_string, has_item,
                      has_entry, is_not, empty)  # noqa H301
from neutronclient.common import exceptions as neutron_exceptions
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
