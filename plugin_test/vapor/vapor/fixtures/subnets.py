# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import pycontrail.types as types
import pytest


@pytest.fixture
def contrail_create_subnet(contrail_api_client):

    networks = []

    def _contrail_create_subnet(network,
                                ipam=None,
                                ip_prefix='10.0.0.0',
                                ip_prefix_len=24):
        networks.append((network, ipam))
        subnet_type = types.SubnetType(
            ip_prefix=ip_prefix, ip_prefix_len=ip_prefix_len)
        vn_sub = types.VnSubnetsType(
            [types.IpamSubnetType(subnet=subnet_type)])
        network.add_network_ipam(ipam, vn_sub)
        contrail_api_client.virtual_network_update(network)

        return

    yield _contrail_create_subnet

    for network, ipam in networks:
        network.del_network_ipam(ipam)
        contrail_api_client.virtual_network_update(network)


@pytest.fixture
def contrail_subnet(contrail_create_subnet, contrail_default_ipam,
                    contrail_network):
    return contrail_create_subnet(contrail_network, contrail_default_ipam)


@pytest.fixture
def update_port(port_steps):
    def _update_port(subnet_id, **kwargs):
        subnet = port_steps._client.update(subnet_id, **kwargs)
        return subnet['subnet']
    return _update_port


