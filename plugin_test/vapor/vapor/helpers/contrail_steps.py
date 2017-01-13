# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.


def get_server_networks(client, server_id):
    """Return contrail network object on which server booted."""
    for iface in client.virtual_machine_interfaces_list(detail=True):
        for iface_ref in iface.get_virtual_machine_refs() or []:
            if iface_ref['uuid'] == server_id:
                for net_ref in iface.get_virtual_network_refs():
                    yield client.virtual_network_read(id=net_ref['uuid'])
