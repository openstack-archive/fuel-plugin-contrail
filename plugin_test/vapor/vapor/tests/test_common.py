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
from stepler.third_party import utils
from pycontrail import exceptions


def test_network_deleting_with_server(network, server, contrail_api_client):
    assert_that(
        calling(contrail_api_client.virtual_network_delete).with_args(
            id=network['id']),
        raises(exceptions.RefsExistError))


def test_create_vm_bulk(net_subnet_router, tiny_flavor,
                        create_servers_context, cirros_image,
                        keypair, security_group):
    network, _, _ = net_subnet_router
    BULK_SERVER_COUNT = 10
    server_names = []
    for sc in xrange(BULK_SERVER_COUNT):
        server_names.append(
            next(utils.generate_ids(prefix='server',
                                    postfix=tiny_flavor.name)))

    with create_servers_context(server_names=server_names,
                                image=cirros_image,
                                flavor=tiny_flavor,
                                networks=[network],
                                keypair=keypair,
                                security_groups=[security_group]):
        pass
