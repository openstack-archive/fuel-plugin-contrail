import time

import pytest
from stepler import config as stepler_config

from vapor import settings

pytestmark = pytest.mark.destructive


def restart_nodes(os_faults_steps, nodes):
    for node in nodes:
        node = os_faults_steps.get_nodes(fqdns=[node.fqdn])
        node.poweroff()
        time.sleep(settings.CONTRAIL_CONTROLLER_RESTART_TIMEOUT)
        node.poweron()


def stop_network_interfaces(os_faults_steps, nodes):
    for node in nodes:
        node = os_faults_steps.get_nodes(fqdns=[node.fqdn])
        node.disconnect(network_name='management')
        node.disconnect(network_name='private')
        time.sleep(settings.CONTRAIL_CONTROLLER_NET_REPLUG_TIMEOUT)
        node.connect(network_name='private')
        node.connect(network_name='management')


@pytest.mark.parametrize('action',
                         [restart_nodes, stop_network_interfaces],
                         ids=['restart', 'stop_network'])
def test_with_destructive_action(
        public_network,
        cirros_image,
        flavor,
        security_group,
        network,
        subnet,
        contrail_controllers,
        create_floating_ip,
        port_steps,
        server_steps,
        os_faults_steps,
        action):

    server1, server2 = server_steps.create_servers(
        count=2,
        image=cirros_image,
        flavor=flavor,
        networks=[network],
        security_groups=[security_group],
        username=stepler_config.CIRROS_USERNAME,
        password=stepler_config.CIRROS_PASSWORD)

    server1_port = port_steps.get_port(
        device_owner=stepler_config.PORT_DEVICE_OWNER_SERVER,
        device_id=server1.id)
    floating_ip = create_floating_ip(public_network, port=server1_port)
    server2_ip = server_steps.get_fixed_ip(server2)
    with server_steps.get_server_ssh(
            server1, ip=floating_ip['floating_ip_address']) as server1_ssh:
        with server_steps.check_ping_loss_context(server2_ip, 0, server1_ssh):
            action(os_faults_steps, contrail_controllers)
