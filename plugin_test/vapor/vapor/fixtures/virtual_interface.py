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
def create_virtual_interface(contrail_api_client, contrail_current_project):
    """Callable fixture to create virtual machine interface(port)."""

    ifaces = []

    def _create(network):
        iface_name, = utils.generate_ids()
        iface = types.VirtualMachineInterface(
            name=iface_name, parent_obj=contrail_current_project)
        iface.add_virtual_network(network)
        ifaces.append(iface)
        contrail_api_client.virtual_machine_interface_create(iface)
        return iface

    yield _create

    for iface in reversed(ifaces):
        try:
            contrail_api_client.virtual_machine_interface_delete(id=iface.uuid)
        except exceptions.NoIdError:
            pass
