# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from hamcrest import assert_that, calling, raises
from pycontrail import exceptions
from pycontrail import types
from stepler import config as stepler_config
from stepler.third_party import utils

from vapor import settings
from vapor.helpers import connectivity


def test_delete_policy_associated_with_network(
        contrail_network, contrail_network_policy, set_network_policy,
        contrail_api_client):
    """Associate/Disassociate/Delete with reference policy using API.

    Steps:
        #. Create network
        #. Create policy
        #. Associate policy with network
        #. Check that deleting network with policy raises an Exception
    """
    set_network_policy(contrail_network, contrail_network_policy)
    assert_that(
        calling(contrail_api_client.network_policy_delete).with_args(
            id=contrail_network_policy.uuid),
        raises(exceptions.RefsExistError))


def test_policy_with_local_source(
        contrail_default_ipam,
        public_network,
        flavor,
        cirros_image,
        security_group,
        contrail_network_policy,
        create_contrail_network,
        create_floating_ip,
        contrail_create_subnet,
        set_network_policy,
        server_steps,
        port_steps,
        contrail_api_client, ):
    """Test policy with local source port and attached to multiple VN.

    Steps:
        #. Create policy with allow ICMP rule for `local` source network
        #. Create 3 networks with subnets
        #. Boot nova server on each network
        #. Check ping from all of servers to first
    """
    rule = types.PolicyRuleType(
        action_list=types.ActionListType(simple_action='pass'),
        direction='<>',
        protocol='icmp',
        src_addresses=[types.AddressType(virtual_network='local')],
        src_ports=[types.PortType()],
        dst_addresses=[types.AddressType(virtual_network='any')],
        dst_ports=[types.PortType()])
    contrail_network_policy.set_network_policy_entries(
        types.PolicyEntriesType(policy_rule=[rule]))
    contrail_api_client.network_policy_update(contrail_network_policy)

    servers = []
    for i, name in enumerate(utils.generate_ids(count=3)):
        network = create_contrail_network(name)
        contrail_create_subnet(
            network,
            ipam=contrail_default_ipam,
            ip_prefix="10.{}.0.0".format(i))
        set_network_policy(network, contrail_network_policy)
        server = server_steps.create_servers(
            flavor=flavor,
            image=cirros_image,
            networks=[{
                'id': network.uuid
            }],
            security_groups=[security_group],
            username=stepler_config.CIRROS_USERNAME,
            password=stepler_config.CIRROS_PASSWORD)[0]
        servers.append(server)

        # Add floating IP addresses
        port = port_steps.get_port(
            device_owner=stepler_config.PORT_DEVICE_OWNER_SERVER,
            device_id=server.id)
        floating_ip = create_floating_ip(public_network, port=port)
        server_steps.check_server_ip(
            server,
            floating_ip['floating_ip_address'],
            timeout=settings.FLOATING_IP_BIND_TIMEOUT)

    # Check pings
    ip = server_steps.get_fixed_ip(servers[0])
    for server in servers[1:]:
        with server_steps.get_server_ssh(server) as server_ssh:
            connectivity.check_icmp_connection_status(ip, remote=server_ssh)
