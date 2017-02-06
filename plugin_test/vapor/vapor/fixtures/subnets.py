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


def _get_ipam_refs(network):
    for ipam_ref in network.get_network_ipam_refs() or []:
        yield ipam_ref


def _get_subnets(network):
    for ipam_ref in _get_ipam_refs(network):
        for subnet in ipam_ref['attr'].ipam_subnets:
            yield subnet


@pytest.fixture
def contrail_create_subnet(contrail_api_client, contrail_default_ipam):
    """Callable fixture to create subnet and delete it after test."""

    networks = []

    def _contrail_create_subnet(network,
                                ipam=None,
                                ip_prefix='10.0.0.0',
                                ip_prefix_len=24):
        # Refresh network data
        network = contrail_api_client.virtual_network_read(id=network.uuid)
        ipam = ipam or contrail_default_ipam

        ipam_subnets = []
        update_exists = False
        for ipam_ref in _get_ipam_refs(network):
            if ipam_ref['uuid'] == ipam.uuid:
                ipam_subnets = ipam_ref['attr'].ipam_subnets
                update_exists = True

        # Store subnet uuids before adding new
        subnet_uuids = {
            x.subnet_uuid
            for x in _get_subnets(network) if x.subnet_uuid is not None
        }

        networks.append((network, ipam))

        subnet_type = types.SubnetType(
            ip_prefix=ip_prefix, ip_prefix_len=ip_prefix_len)
        ipam_subnets.append(types.IpamSubnetType(subnet=subnet_type))
        vn_sub = types.VnSubnetsType(ipam_subnets=ipam_subnets)
        if update_exists:
            network.set_network_ipam(ipam, vn_sub)
        else:
            network.add_network_ipam(ipam, vn_sub)
        contrail_api_client.virtual_network_update(network)

        # Reread network data after update
        network = contrail_api_client.virtual_network_read(id=network.uuid)
        for subnet in _get_subnets(network):
            if subnet.subnet_uuid not in subnet_uuids:
                break
        return subnet

    yield _contrail_create_subnet

    for network, ipam in networks:
        network.del_network_ipam(ipam)
        contrail_api_client.virtual_network_update(network)


@pytest.fixture
def contrail_subnet(contrail_create_subnet, contrail_default_ipam,
                    contrail_network):
    return contrail_create_subnet(contrail_network, contrail_default_ipam)
