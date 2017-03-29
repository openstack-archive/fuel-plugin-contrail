# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from hamcrest import assert_that, is_not
import pytest
from stepler import config as stepler_config
from stepler.third_party import waiter

from vapor import settings
from vapor.helpers.asserts import intersects_with
from vapor.helpers import analytic_steps
from vapor.helpers import contrail_status

pytestmark = pytest.mark.destructive


def test_connectivity_after_restart_compute(server, public_network,
                                            create_floating_ip, port_steps,
                                            server_steps, os_faults_steps):
    """Test nova server connectivity after restart compute.

    Steps:
        #. Create nova server
        #. Assign Floating IP to server
        #. Check that ping to Floating IP is success
        #. Power off and power on compute and wait for compute to boot
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
    server_steps.check_ping_for_ip(ip, timeout=settings.PING_SUCCESS_TIMEOUT)

    # Restart compute
    compute_host = getattr(server, stepler_config.SERVER_ATTR_HOST)
    compute_fqdn = os_faults_steps.get_fqdn_by_host_name(compute_host)
    compute_node = os_faults_steps.get_nodes(fqdns=[compute_fqdn])

    # Flush file system buffers
    os_faults_steps.execute_cmd(compute_node, 'sync')
    # Restart node
    os_faults_steps.poweroff_nodes(compute_node)
    os_faults_steps.poweron_nodes(compute_node)

    # Check ping again
    server_steps.check_ping_for_ip(ip, timeout=settings.PING_SUCCESS_TIMEOUT)


@pytest.mark.requires("vrouter_headless_mode")
def test_connectivity_during_restart_controllers(
        server, public_network, create_floating_ip, port_steps, server_steps,
        os_faults_steps):
    """Test nova server connectivity during restart controllers.

    Steps:
        #. Create nova server
        #. Assign Floating IP to server
        #. Start background ping to Floating IP
        #. Power off and power on contrail controller nodes and wait for them
            to be available
        #. Stop background ping and check that there is no ping losses
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
    for i in range(30):
        server_steps.check_ping_for_ip(
            ip, timeout=settings.PING_SUCCESS_TIMEOUT)

    # Get contrail controller nodes
    controlles_fqdns = settings.CONTRAIL_ROLES_DISTRIBUTION[
        settings.ROLE_CONTRAIL_CONTROLLER]
    controllers = os_faults_steps.get_nodes(fqdns=controlles_fqdns)

    # Start background ping to Floating IP
    with server_steps.check_ping_loss_context(ip):
        # Restart nodes
        os_faults_steps.poweroff_nodes(controllers)
        os_faults_steps.poweron_nodes(controllers)
        server_steps.check_ping_for_ip(
            ip, timeout=settings.PING_SUCCESS_TIMEOUT)


def test_connectivity_after_contrail_services_restart(
        request, server, public_network, create_floating_ip, port_steps,
        server_steps, os_faults_steps):
    """Test nova server connectivity after restart contrail services.

    Steps:
        #. Create nova server
        #. Assign Floating IP to server
        #. Check that ping to Floating IP is success
        #. Restart all contrail services
        #. Check that ping to Floating IP is success
        #. Verify network creation with Contrail API
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
    server_steps.check_ping_for_ip(ip, timeout=settings.PING_SUCCESS_TIMEOUT)

    cmd = ("PIDS=$(ps aux | awk '/awk/ {next} /contrail/{print $2}')\n"
           "if [ $PIDS ]; then kill $PIDS; fi")
    nodes = os_faults_steps.get_nodes()
    os_faults_steps.execute_cmd(nodes, cmd)

    # Check ping again
    server_steps.check_ping_for_ip(ip, timeout=settings.PING_SUCCESS_TIMEOUT)

    # Verify network creation
    network = request.getfixturevalue('contrail_network')
    assert_that(network.uuid, is_not(None))


def test_agent_cleanup_with_control_node_stop(
        session, nodes_ips, contrail_services_http_introspect_ports,
        cirros_image, flavor, security_group, network, subnet, public_network,
        create_floating_ip, stop_service, port_steps, server_steps,
        os_faults_steps):
    """Stop all the control node and verify the cleanup process in agent.

    Steps:
        #. Create network, subnet
        #. Create 2 servers
        #. Add floating IP addresses to servers
        #. Check ping to servers' floating ips
        #. Get servers' ids from contrail_vrouter_agent
        #. Get contrail control nodes connected to this contrail_vrouter_agent
        #. Stop `contrail-control` service on found nodes
        #. Check that servers' ids list from contrail_vrouter_agent is not
            contain servers ids after some time
        #. Start `contrail-control` service on found nodes
        #. Check that servers' ids list from contrail_vrouter_agent is contain
            servers ids after some time
        #. Check ping to servers' floating ips
    """
    # Create servers
    servers = server_steps.create_servers(
        count=2,
        image=cirros_image,
        flavor=flavor,
        security_groups=[security_group],
        networks=[network],
        username=stepler_config.CIRROS_USERNAME,
        password=stepler_config.CIRROS_PASSWORD)

    # Create Floating IP
    for server in servers:
        server_port = port_steps.get_port(
            device_owner=stepler_config.PORT_DEVICE_OWNER_SERVER,
            device_id=server.id)

        floating_ip = create_floating_ip(public_network, port=server_port)
        server_steps.check_server_ip(
            server,
            floating_ip['floating_ip_address'],
            timeout=settings.FLOATING_IP_BIND_TIMEOUT)

    for server in servers:
        server_steps.check_ping_to_server_floating(
            server, timeout=stepler_config.PING_CALL_TIMEOUT)

    servers_ids = [s.id for s in servers]
    compute_fqdn = getattr(servers[0],
                           settings.SERVER_ATTR_HYPERVISOR_HOSTNAME)
    agent_ip = nodes_ips[compute_fqdn][0]
    agent_port = contrail_services_http_introspect_ports[
        'contrail-vrouter-agent']['port']

    analytic_steps.wait_vna_vm_list(
        session, agent_ip, agent_port,
        intersects_with(servers_ids),
        settings.CONTRAIL_AGENT_VNA_VM_LIST_TIMEOUT)

    # Collecting control nodes
    controllers_fqdns = []
    for entry in analytic_steps.get_vna_xmpp_connection_status(
            session, agent_ip, agent_port):
        ip = entry['controller_ip']
        fqdn = next(fqnd for fqnd, ips in nodes_ips.items() if ip in ips)
        controllers_fqdns.append(fqdn)
    controller_nodes = os_faults_steps.get_nodes(fqdns=controllers_fqdns)

    # Stop contrail-control service
    stop_service(controller_nodes, 'contrail-control')

    analytic_steps.wait_vna_vm_list(session, agent_ip, agent_port,
                                    is_not(intersects_with(servers_ids)),
                                    settings.CONTRAIL_AGENT_CLEANUP_TIMEOUT)

    os_faults_steps.execute_cmd(controller_nodes,
                                'service contrail-control start')

    analytic_steps.wait_vna_vm_list(
        session, agent_ip, agent_port,
        intersects_with(servers_ids),
        settings.CONTRAIL_AGENT_VNA_VM_LIST_TIMEOUT)

    for server in servers:
        server_steps.check_ping_to_server_floating(
            server, timeout=stepler_config.PING_CALL_TIMEOUT)


@pytest.mark.requires('contrail_control_nodes_count >= 2')
def test_contrail_services_status_after_restart_master_node(os_faults_steps):
    """Verify contrail services status after master node restart.

    Steps:
        #. Restart node with contrail-schema (active)
        #. Wait some time
        #. Check that contrail services statuses is correct
    """
    services_statuses = contrail_status.get_services_statuses(os_faults_steps)
    master_node_fqdn = None
    for fqdn, services in services_statuses.items():
        for service in services:
            if (service['service'] == 'contrail-schema' and
                    service['status'] == contrail_status.STATUS_ACTIVE):
                master_node_fqdn = fqdn
                break
    assert master_node_fqdn is not None, "Can't find master node"
    master_node = os_faults_steps.get_node(fqdns=[master_node_fqdn])
    os_faults_steps.reset_nodes(master_node)

    waiter.wait(
        contrail_status.check_services_statuses,
        args=(os_faults_steps),
        expected_exceptions=AssertionError,
        timeout=settings.CONTRAIL_NODE_RESET_TIMEOUT)
