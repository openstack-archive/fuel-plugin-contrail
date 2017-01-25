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
from stepler import config as stepler_config

from vapor import settings

pytestmark = pytest.mark.destructive


def test_connectivity_after_restart_compute(server, public_network,
                                            create_floating_ip, port_steps,
                                            server_steps, os_faults_steps):
    """Test nova server connectivity after restart compute.

    Steps:
        #. Create nova server
        #. Assign Floating IP to server
        #. Check that ping to Floating IP is success
        #. Power off and power on compute
        #. Wait for compute to boot
        #. Check that ping to Floating IP is success
    """
    compute_host = getattr(server, stepler_config.SERVER_ATTR_HOST)
    compute_fqdn = os_faults_steps.get_fqdn_by_host_name(compute_host)
    compute_node = os_faults_steps.get_nodes(fqdns=[compute_fqdn])
    server_port = port_steps.get_port(
        device_owner=stepler_config.PORT_DEVICE_OWNER_SERVER,
        device_id=server.id)

    # Create Floating IP
    floating_ip = create_floating_ip(public_network, port=server_port)
    ip = floating_ip['floating_ip_address']
    server_steps.check_server_ip(
        server, ip, timeout=settings.FLOATING_IP_BIND_TIMEOUT)

    # Check ping to Floating IP
    server_steps.check_ping_for_ip(ip, timeout=settings.PING_SUCESS_TIMEOUT)\

    # Flush file system buffers
    os_faults_steps.execute_cmd(compute_node, 'sync')
    # Restart node
    os_faults_steps.poweroff_nodes(compute_node)
    os_faults_steps.poweron_nodes(compute_node)

    # Check ping again
    server_steps.check_ping_for_ip(ip, timeout=settings.PING_SUCESS_TIMEOUT)
