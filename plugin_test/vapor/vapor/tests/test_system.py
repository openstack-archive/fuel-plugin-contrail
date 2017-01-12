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

from hamcrest import assert_that, has_length, has_items, has_entries
from stepler import config as stepler_config

from vapor.helpers import nodes_steps


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
    assert_that(after_interfaces[compute_fqdn] -
                before_interfaces[compute_fqdn], has_length(2))

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
