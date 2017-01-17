# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from hamcrest import assert_that, calling, raises  # noqa H301
from pycontrail import exceptions
from neutronclient.common import exceptions as neutron_exceptions


def test_network_deleting_with_server(network, server, contrail_api_client):
    assert_that(
        calling(contrail_api_client.virtual_network_delete).with_args(
            id=network['id']),
        raises(exceptions.RefsExistError))


def test_create_vm_bulk(net_subnet_router, tiny_flavor,
                        cirros_image, server_steps):
    network, _, _ = net_subnet_router
    BULK_SERVER_COUNT = 10
    servers = server_steps.create_servers(count=BULK_SERVER_COUNT,
                                          image=cirros_image,
                                          flavor=tiny_flavor,
                                          networks=[network])
    server_steps.delete_servers(servers)


def test_delete_vm_with_associated_vn(contrail_network, contrail_subnet,
                                      tiny_flavor, cirros_image,
                                      server_steps, network_steps):
    servers = server_steps.create_servers(
        count=1, image=cirros_image, flavor=tiny_flavor,
        nics=[{'net-id': contrail_network.uuid}])
    net = network_steps.get_network(id=contrail_network.uuid)
    assert_that(calling(network_steps.delete).with_args(net),
                raises(neutron_exceptions.NetworkInUseClient))
    server_steps.delete_servers(servers)
