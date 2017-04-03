# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import attrdict
import pytest
from stepler import config as stepler_config
from stepler.third_party import utils

from vapor import settings


@pytest.fixture
def contrail_2_networks(create_network, create_subnet):
    """Function fixture to prepare environment with 2 networks.

    This fixture creates 2 networks and 2 subnets.
    """
    names = list(utils.generate_ids(count=2))
    networks = []
    subnets = []
    cidrs = ['10.0.0.0/24', '10.0.1.0/24']
    for name, cidr in zip(names, cidrs):
        network = create_network(name)
        networks.append(network)
        subnet = create_subnet(name + '__subnet', network=network, cidr=cidr)
        subnets.append(subnet)
    return attrdict.AttrDict(networks=networks, subnets=subnets)


@pytest.fixture
def contrail_2_servers_different_networks(
        request,
        vapor_flavor,
        neutron_security_group,
        sorted_hypervisors,
        contrail_2_networks,
        server_steps):
    """Function fixture to prepare environment with 2 servers.

    This fixture creates 2 networks and 2 subnets, boot nova server on each
    network on different computes.

    All created resources are to be deleted after test.

    Can be parametrized with dict.

    Example:
        @pytest.mark.parametrize('contrail_2_servers_different_networks',
                                 [dict(same_host=True)],
                                 indirect=True)
        def test_foo(contrail_2_servers_different_networks):
            # Instances will be created on the same compute
    """
    params = dict(
        same_host=False,
        ubuntu=False
    )
    hypervisors = sorted_hypervisors[:2]
    new_params = getattr(request, 'param', {})
    params.update(new_params)

    if params['same_host']:
        hypervisors[1] = hypervisors[0]

    if params['ubuntu']:
        image = request.getfixturevalue('ubuntu_image')
        keypair = request.getfixturevalue('keypair')
        username = stepler_config.UBUNTU_USERNAME
        password = None
    else:
        image = request.getfixturevalue('cirros_image')
        keypair = None
        username = stepler_config.CIRROS_USERNAME
        password = stepler_config.CIRROS_PASSWORD

    servers = []

    for hypervisor, network in zip(hypervisors, contrail_2_networks.networks):
        server = server_steps.create_servers(
            image=image,
            flavor=vapor_flavor,
            networks=[network],
            keypair=keypair,
            availability_zone='nova:{}'.format(hypervisor.service['host']),
            security_groups=[neutron_security_group],
            username=username,
            password=password,
            check=False)[0]
        servers.append(server)

    for server in servers:

        server_steps.check_server_status(
            server,
            expected_statuses=[stepler_config.STATUS_ACTIVE],
            transit_statuses=[stepler_config.STATUS_BUILD],
            timeout=stepler_config.SERVER_ACTIVE_TIMEOUT)

    return attrdict.AttrDict(
        servers=servers,
        networks=contrail_2_networks.networks,
        subnets=contrail_2_networks.subnets)


@pytest.fixture
def contrail_2_servers_diff_nets_with_floating(
        contrail_2_servers_different_networks,
        public_network,
        create_floating_ip,
        server_steps,
        port_steps):
    """Function fixture to prepare environment with 2 servers.

    This fixture creates resources using contrail_2_servers_different_networks
    fixture, creates and attaches floating ips for all servers.

    All created resources are to be deleted after test.
    """
    resources = contrail_2_servers_different_networks

    floating_ips = []
    for server in resources.servers:
        port = port_steps.get_port(
            device_owner=stepler_config.PORT_DEVICE_OWNER_SERVER,
            device_id=server.id)
        floating_ip = create_floating_ip(public_network, port=port)
        server_steps.check_server_ip(
            server,
            floating_ip['floating_ip_address'],
            timeout=settings.FLOATING_IP_BIND_TIMEOUT)
        floating_ips.append(floating_ip)

    resources.floating_ips = floating_ips

    return resources
