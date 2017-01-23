# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from pycontrail import exceptions
import pycontrail.types as types
import pytest
from stepler.third_party import utils


@pytest.fixture
def contrail_ipams_cleanup(contrail_api_client):
    """Cleanup created ipams after test."""

    def _get_ipams_uuids():
        return {
            ipam['uuid']
            for ipam in contrail_api_client.network_ipams_list()[
                'network-ipams']
        }

    before = _get_ipams_uuids()

    yield

    for ipam_uuid in _get_ipams_uuids() - before:
        contrail_api_client.network_ipam_delete(id=ipam_uuid)


@pytest.fixture
def contrail_ipam(contrail_api_client):
    name, = utils.generate_ids()
    ipam = types.NetworkIpam(name)
    contrail_api_client.network_ipam_create(ipam)
    yield ipam
    try:
        contrail_api_client.network_ipam_delete(id=ipam.uuid)
    except exceptions.NoIdError:
        pass
