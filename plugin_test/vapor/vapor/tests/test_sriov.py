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
from vapor import settings

pytestmark = pytest.mark.requires('sriov_enabled')


def test_virtual_function_exhaustion_and_reuse(
        ubuntu_xenial_image, flavor, network, subnet, net_subnet_router,
        neutron_security_group, floating_ip, keypair, create_network,
        create_subnet, create_port, os_faults_steps, computes,
        floating_ip_steps, server_steps, nova_availability_zone_hosts):
    """Verify Nova can schedule VM to all the VF of a PF.

    Steps:
        #. Create management network with subnet
        #. Create SRIOV network and subnet
        #. Get total_vfs parameter for SRIOV interface
        #. Create 1 port for management network and 1 port for SRIOV network
        #. Boot server with created 2 ports, check that is reaches ACTIVE
            status
        #. Create 1 port for SRIOV network
        #. Repeat last 2 steps `total_vfs` - 1 times
        #. Check ping from 1st server to all another
        #. Create 1 port for management network and 1 port for SRIOV network
        #. Create another one server with created 2 ports
        #. Check that server reaches ERROR status
        #. Delete last created server
        #. Delete first created server
        #. Create 1 port for management network and 1 port for SRIOV network
        #. Create another one server with created 2 ports, check that is
            reaches ACTIVE status
    """
    sriov_devices = sriov.get_sriov_devices(os_faults_steps, computes)
    compute_name, ifaces = next(six.iteritems(sriov_devices))
    sriov_iface = next(six.iterkeys(ifaces))
    numvfs = ifaces[sriov_iface]['sriov_numvfs']

    # Find availability zone compute host
    compute_host = next(
        host for host in nova_availability_zone_hosts
        if compute_name.startswith(host))

    # Create SRIOV net and subnet
    kwargs = {
        'provider:network_type': 'vlan',
        'provider:physical_network': settings.SRIOV_PHYSNET,
        'provider:segmentation_id': 200
    }
    sriov_net_name, = utils.generate_ids()
    sriov_net = create_network(sriov_net_name, **kwargs)
    create_subnet(
        sriov_net_name + '__subnet', sriov_net, cidr="10.200.54.0/24")

    # Create servers
    servers = []
    sriov_port_kwargs = {
        'binding:vnic_type': 'direct',
        'security_groups': [neutron_security_group['id']]
    }
    server_create_args = dict(
        image=ubuntu_xenial_image,
        flavor=flavor,
        availability_zone='nova:{}'.format(compute_host),
        keypair=keypair,
        username=stepler_config.UBUNTU_USERNAME)
    for i in range(numvfs):
        sriov_port = create_port(sriov_net, **sriov_port_kwargs)
        ports = [sriov_port]
        if i == 0:
            mgmt_port = create_port(
                network, security_groups=[neutron_security_group['id']])
            ports.insert(0, mgmt_port)
        server = server_steps.create_servers(
            ports=ports, **server_create_args)[0]
        servers.append(server)
        if i == 0:
            floating_ip_steps.attach_floating_ip(floating_ip, mgmt_port)

    # Check ping between servers
    ping_plan = {servers[0]: servers[1:]}
    server_steps.check_ping_by_plan(
        ping_plan, timeout=stepler_config.PING_BETWEEN_SERVERS_TIMEOUT)

    # Try to create one more server
    mgmt_port = create_port(network)
    sriov_port = create_port(sriov_net, **sriov_port_kwargs)

    error_server = server_steps.create_servers(
        ports=[mgmt_port, sriov_port], check=False, **server_create_args)[0]
    server_steps.check_server_status(
        error_server, [stepler_config.STATUS_ERROR],
        transit_statuses=[stepler_config.STATUS_BUILD],
        timeout=stepler_config.SERVER_ACTIVE_TIMEOUT)

    # Delete last created server on error status
    server_steps.delete_servers([error_server])

    # Delete first created server
    server_steps.delete_servers(servers[:1])

    # Create another server
    sriov_port = create_port(sriov_net, **sriov_port_kwargs)

    server_steps.create_servers(ports=[sriov_port], **server_create_args)[0]
