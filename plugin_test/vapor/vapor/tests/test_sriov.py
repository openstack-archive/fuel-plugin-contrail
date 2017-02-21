# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import pytest
import six
from stepler import config as stepler_config
from stepler.third_party import utils

from vapor.helpers import sriov

pytestmark = pytest.mark.requires('sriov_enabled')


def test_virtual_function_exhaustion_and_reuse(
        cirros_image, flavor, network, subnet, create_network, create_subnet,
        create_port, agent_steps, os_faults_steps, server_steps):
    """Verify Nova can schedule VM to all the VF of a PF.

    Steps:
        #. Create management network with subnet
        #. Create SRIOV network and subnet
        #. Get total_vfs parameter for SRIOV interface
        #. Create 1 port for management network and 1 port for SRIOV network
        #. Boot server with created 2 ports, check that is reaches ACTIVE
            status
        #. Repeat last 2 steps `total_vfs` times
        #. Create 1 port for management network and 1 port for SRIOV network
        #. Create another one server with created 2 ports
        #. Check that server reaches ERROR status
        #. Delete last created server
        #. Delete first created server
        #. Create 1 port for management network and 1 port for SRIOV network
        #. Create another one server with created 2 ports, check that is
            reaches ACTIVE status
    """
    sriov_device_mappings = sriov.get_sriov_device_mapping(agent_steps)
    compute_name, device_mapping = next(six.iteritems(sriov_device_mappings))
    sriov_physnet = next(six.iterkeys(device_mapping))
    sriov_iface = device_mapping[sriov_physnet][0]
    numvfs = sriov.get_sriov_numvfs(os_faults_steps, compute_name, sriov_iface)

    # Create SRIOV net and subnet
    kwargs = {
        'provider:network_type': 'vlan',
        'provider:physical_network': sriov_physnet,
        'provider:segmentation_id': 200
    }
    sriov_net_name, = utils.generate_ids()
    sriov_net = create_network(sriov_net_name, **kwargs)
    create_subnet(sriov_net_name + '__subnet', sriov_net, cidr="55.1.1.0/24")

    # Create servers
    servers = []
    sriov_port_kwargs = {'binding:vnic_type': 'direct'}
    server_create_args = dict(
        image=cirros_image,
        flavor=flavor,
        availability_zone='nova:{}'.format(compute_name))
    for _ in range(numvfs):
        mgmt_port = create_port(network)
        sriov_port = create_port(sriov_net, **sriov_port_kwargs)
        server = server_steps.create_servers(
            ports=[mgmt_port, sriov_port], **server_create_args)[0]
        servers.append(server)

    # Try to create one more server
    mgmt_port = create_port(network)
    sriov_port = create_port(sriov_net, **sriov_port_kwargs)

    error_server = server_steps.create_servers(
        ports=[mgmt_port, sriov_port], check=False, **server_create_args)[0]
    server_steps.check_server_status(
        error_server,
        [stepler_config.STATUS_ERROR],
        transit_statuses=[stepler_config.STATUS_BUILD],
        timeout=stepler_config.SERVER_ACTIVE_TIMEOUT)

    # Delete last created server on error status
    server_steps.delete_servers([error_server])

    # Delete first created server
    server_steps.delete_servers(servers[:1])

    # Create another server
    mgmt_port = create_port(network)
    sriov_port = create_port(sriov_net, **sriov_port_kwargs)

    server_steps.create_servers(
        ports=[mgmt_port, sriov_port], **server_create_args)[0]
