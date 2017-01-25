# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import types

import attrdict
import pytest
from stepler import config as stepler_config

from vapor import settings

pytestmark = pytest.mark.destructive


def restart_compute(args):
    compute_host = getattr(args.server, stepler_config.SERVER_ATTR_HOST)
    compute_fqdn = args.os_faults_steps.get_fqdn_by_host_name(compute_host)
    compute_node = args.os_faults_steps.get_nodes(fqdns=[compute_fqdn])

    # Flush file system buffers
    args.os_faults_steps.execute_cmd(compute_node, 'sync')
    # Restart node
    args.os_faults_steps.poweroff_nodes(compute_node)
    args.os_faults_steps.poweron_nodes(compute_node)


def restart_contrail_controllers(args):
    controlles_fqdns = settings.CONRTAIL_ROLES_DISTRIBUTION[
        settings.ROLE_CONTRAIL_CONTROLLER]

    controllers = args.os_faults_steps.get_nodes(fqdns=controlles_fqdns)
    # Restart node
    args.os_faults_steps.poweroff_nodes(controllers)
    args.os_faults_steps.poweron_nodes(controllers)


def restart_contrail_services(args):
    cmd = ("PIDS=$(ps aux | awk '/awk/ {next} /contrail/{print $2}')\n"
           "if [ $PIDS ]; then kill $PIDS; fi")
    nodes = args.os_faults_steps.get_nodes()
    args.os_faults_steps.execute_cmd(nodes, cmd)


def idfn(val):
    if isinstance(val, types.FunctionType):
        return val.func_name


@pytest.mark.parametrize(
    'action',
    [restart_compute, restart_contrail_controllers, restart_contrail_services],
    ids=idfn)
def test_connectivity_after_destructive_action(
        server, public_network, create_floating_ip, port_steps, server_steps,
        os_faults_steps, action):
    """Test nova server connectivity after restart compute.

    Steps:
        #. Create nova server
        #. Assign Floating IP to server
        #. Check that ping to Floating IP is success
        #. Perform one of destructive actions:
            * Power off and power on compute and wait for compute to boot
        #. Check that ping to Floating IP is success
    """
    server_port = port_steps.get_port(
        device_owner=stepler_config.PORT_DEVICE_OWNER_SERVER,
        device_id=server.id)

    # Create Floating IP
    floating_ip = create_floating_ip(public_network, port=server_port)
    ip = floating_ip['floating_ip_address']
    server_steps.check_server_ip(
        server, ip, timeout=settings.FLOATING_IP_BIND_TIMEOUT)

    # Check ping to Floating IP
    server_steps.check_ping_for_ip(ip, timeout=settings.PING_SUCESS_TIMEOUT)

    args = attrdict.AttrDict(os_faults_steps=os_faults_steps, server=server)

    # Perform destructive action
    action(args)

    # Check ping again
    server_steps.check_ping_for_ip(ip, timeout=settings.PING_SUCESS_TIMEOUT)
