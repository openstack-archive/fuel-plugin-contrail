# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import itertools
import time

from hamcrest import assert_that, has_length, has_items, has_entries, equal_to
from stepler import config as stepler_config

from vapor.helpers import contrail_steps
from vapor.helpers import nodes_steps
from vapor import settings


def test_no_connectivity_between_vms_in_different_tenants(
        request, contrail_api_client, os_faults_steps):
    """Check no connectivity between VMs in different tenants.

    Steps:
        #. Create 2 new tenants (the tenant networks under test must have
            intersecting or the same IP address spaces and the must be no
            policy enabled, which allows the traffic between tenants)
        #. Launch 2 new instance in different tenants
        #. Check that no ping connectivity between instances
        #. Connect to Compute Node via SSH and check that VMs has different
            ethernet device
        #. Verify with contrail API that networks are present and VMs are
            attached to different networks.
    """
    # Store nodes interfaces
    before_interfaces = nodes_steps.get_nodes_interfaces(os_faults_steps)

    resources = request.getfixturevalue('different_tenants_resources')
    # Check that there is no ping between tenants
    for resources1, resources2 in itertools.permutations(resources):
        ip_to_ping = resources1.server_steps.get_fixed_ip(resources1.server)
        server_steps = resources2.server_steps
        floating_ip = resources2.floating_ip['floating_ip_address']
        with server_steps.get_server_ssh(
                resources2.server, ip=floating_ip) as server_ssh:
            with server_steps.check_no_ping_context(
                    ip_to_ping, server_ssh=server_ssh):
                time.sleep(5)

    # Get interfaces list again
    after_interfaces = nodes_steps.get_nodes_interfaces(os_faults_steps)
    compute_fqdn = getattr(resources[0].server,
                           stepler_config.SERVER_ATTR_HOST)

    # Check that there is 2 interfaces on compute - one for each VM
    assert_that(
        after_interfaces[compute_fqdn] - before_interfaces[compute_fqdn],
        has_length(2))

    # Check that networks are present in contrail
    contrail_networks = contrail_api_client.virtual_networks_list()
    networks_matchers = [
        has_entries(uuid=res.network['id']) for res in resources
    ]
    assert_that(contrail_networks['virtual-networks'],
                has_items(*networks_matchers))

    # Check that VMs attached to different networks
    networks_uuid = set()
    for resource in resources:
        iface = contrail_api_client.virtual_machine_interface_read(
            id=resource.port['id'])
        networks_uuid.add(iface.get_virtual_network_refs()[0]['uuid'])
    assert_that(networks_uuid, has_length(2))


def test_create_network_with_contrail(
        cirros_image, flavor, security_group, contrail_network,
        contrail_subnet, public_network, create_floating_ip,
        contrail_api_client, server_steps, port_steps):
    """Check that OpenStack can operate with network created with Contrail.

    Steps:
        #. Create new network with Contrail API
        #. Launch 2 instances on created network
        #. Check ping between instances
        #. Verify that instances are attached to created network in contrail
    """
    servers = server_steps.create_servers(
        count=2,
        image=cirros_image,
        flavor=flavor,
        nics=[{
            'net-id': contrail_network.uuid
        }],
        security_groups=[security_group],
        username=stepler_config.CIRROS_USERNAME,
        password=stepler_config.CIRROS_PASSWORD)
    for server in servers:
        port = port_steps.get_port(
            device_owner=stepler_config.PORT_DEVICE_OWNER_SERVER,
            device_id=server.id)
        floating_ip = create_floating_ip(public_network, port=port)
        server_steps.check_server_ip(
            server,
            floating_ip['floating_ip_address'],
            timeout=settings.FLOATING_IP_BIND_TIMEOUT)

    # Check ping between instances
    server_steps.check_ping_between_servers_via_floating(
        servers, ip_types=(stepler_config.FIXED_IP, ))

    # Verify that instances are attached to created network in contrail
    networks = set()
    for server in servers:
        for net in contrail_steps.get_server_networks(contrail_api_client,
                                                      server.id):
            networks.add(net.uuid)
    assert_that(networks, equal_to(set([contrail_network.uuid])))
