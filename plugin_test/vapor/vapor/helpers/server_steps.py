# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from stepler import config as stepler_config

from vapor import settings
from vapor.helpers import nodes_steps


def get_server_port(server, port_steps):
    """Return server's port."""
    return port_steps.get_port(
        device_owner=stepler_config.PORT_DEVICE_OWNER_SERVER,
        device_id=server.id)


def get_server_node(server, os_faults_steps):
    """Return server's compute node."""
    node_name = getattr(server, settings.SERVER_ATTR_HYPERVISOR_HOSTNAME)
    return os_faults_steps.get_node(fqdns=[node_name])


def get_server_compute_iface(server, os_faults_steps, port_steps):
    """Return node and tap interface name for server port."""
    port = get_server_port(server, port_steps)
    node = get_server_node(server, os_faults_steps)
    expected_name = 'tap{}'.format(port['id'])
    interfaces = nodes_steps.get_nodes_interfaces(os_faults_steps, node)
    return next(x for x in interfaces if expected_name.startswith(x))
