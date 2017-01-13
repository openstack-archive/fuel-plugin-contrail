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
def contrail_subnet(contrail_api_client, contrail_network):
    ipam_id = contrail_api_client.network_ipam_get_default_id()
    ipam = contrail_api_client.network_ipam_read(id=ipam_id)
    subnet_type = types.SubnetType(ip_prefix='10.0.0.0', ip_prefix_len=24)
    vn_sub = types.VnSubnetsType([types.IpamSubnetType(subnet=subnet_type)])
    contrail_network.add_network_ipam(ipam, vn_sub)
    contrail_api_client.virtual_network_update(contrail_network)

    yield

    contrail_network.del_network_ipam(ipam)
    contrail_api_client.virtual_network_update(contrail_network)
