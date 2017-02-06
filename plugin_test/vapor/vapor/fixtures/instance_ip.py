"""Contrail InstanceIP fixtures."""

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
from pycontrail import exceptions
from pycontrail import types
from stepler.third_party import utils


@pytest.fixture
def contrail_create_instance_ip(contrail_api_client):
    """Fixture to create contrail InstanceIP."""

    ips = []

    def _create(network, iface, ip_address, subnet_uuid=None):
        name, = utils.generate_ids()
        ip = types.InstanceIp(
            name=name, instance_ip_address=ip_address, subnet_uuid=subnet_uuid)
        ip.add_virtual_machine_interface(iface)
        ip.add_virtual_network(network)
        ips.append(ip)
        contrail_api_client.instance_ip_create(ip)
        return ip

    yield _create

    for ip in ips:
        try:
            contrail_api_client.instance_ip_delete(id=ip.uuid)
        except exceptions.NoIdError:
            pass
