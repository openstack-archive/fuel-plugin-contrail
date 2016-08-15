"""Copyright 2016 Mirantis, Inc.

Licensed under the Apache License, Version 2.0 (the "License"); you may
not use this file except in compliance with the License. You may obtain
copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
License for the specific language governing permissions and limitations
under the License.
"""

import subprocess
from fuelweb_test import logger
from devops.helpers.helpers import wait
from devops.helpers.helpers import tcp_ping

from helpers import settings


def vsrx_activate(obj=None, multi_nets=False, upload_config=False):
    """Activate vSRX1 image."""
    def call_cmd(cmd):
        logger.info('The command is %s', cmd)
        subprocess.call(cmd, shell=True)
    logger.info("#" * 10 + 'Configure iptables and route...' + "#" * 10)
    map(call_cmd, [
        'sudo /sbin/iptables -F',
        'sudo /sbin/iptables -t nat -F',
        'sudo /sbin/iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE'])

    if not settings.VSRX_TEMPLATE_PATH:
        logger.info("#" * 10 + 'VSRX_TEMPLATE_PATH is not defined, '
                    'OSTF will not be running' + "#" * 10)
        return False

    logger.info("#" * 10 + 'Delete previous installation of vSRX..' + "#" * 10)
    map(call_cmd, [
        'virsh destroy vSRX1',
        'virsh undefine vSRX1',
        'sed -r "s/ENV_NAME/$ENV_NAME/g" {0} > logs/vSRX1.xml'.format(
            settings.VSRX_TEMPLATE_PATH),
        'sed -i -r "s/vSRX1.img/vSRX.400.img/g" logs/vSRX1.xml',
    ])

    logger.info("#" * 10 + 'Create vSRX...' + "#" * 10)
    if subprocess.call('virsh create logs/vSRX1.xml', shell=True):
        logger.info("#" * 10 + 'VSRX could not be established, '
                    'OSTF will not be running' + "#" * 10)
        return False

    map(call_cmd, [
        'sudo ip route del 10.100.1.0/24',
        'sudo ip route add 10.100.1.0/24 via 10.109.3.250'])

    if multi_nets:
        assert obj, "obj is None"
        vsrx_multiple_networks(multi_nets)
    if upload_config and settings.VSRX_CONFIG_PATH:
        assert obj, "obj is None"
        vsrx_upload_config(obj, config_path=settings.VSRX_CONFIG_PATH)
    return True


def vsrx_multiple_networks(obj, vsrx_ip='10.109.4.250', net_name='private2'):
    """Configure routing on vsrx to no default private network.

    :param obj: Test case object
    :param vsrx_ip: ip of vSRX router
    :param net_name: name of no default private network

    """
    ip_private_net = obj.env.d_env.get_network(name=net_name).ip_network

    ip_private_net_default = obj.env.d_env.get_network(
        name='private').ip_network

    commands = [
        'cli',
        'configure',
        'set protocols bgp group Contrail_Controller allow {0}'.format(
            ip_private_net),
        'set routing-options static route {0} next-hop {1}'.format(
            ip_private_net, ip_private_net_default.split('0/').pop(0) + '1'),
        'delete routing-options static route {0} '.format(
            ip_private_net_default) + 'next-table public.inet.0',
        'set routing-options dynamic-tunnels dynamic_overlay_tunnels'
        ' destination-networks {0}'.format(ip_private_net),
        'commit']

    wait(
        lambda: tcp_ping(vsrx_ip, 22), timeout=60 * 2, interval=10,
        timeout_msg="Node {0} is not accessible by SSH.".format(vsrx_ip))
    with obj.env.d_env.get_ssh_to_remote(vsrx_ip) as remote:
        for command in commands:
            remote.execute_async(command)


def vsrx_upload_config(obj, config_path, vsrx_ip='10.109.4.250'):
    """Upload and commit configuration for VSRX."""
    commands = [
        'cli', 'configure',
        'load override {0}'.format(config_path.split('/').pop()),
        'commit']
    wait(
        lambda: tcp_ping(vsrx_ip, 22), timeout=60 * 2, interval=10,
        timeout_msg="Node {0} is not accessible by SSH.".format(vsrx_ip))
    with obj.env.d_env.get_ssh_to_remote(vsrx_ip) as remote:
        remote.upload(config_path, '/cf/root')
        for command in commands:
            remote.execute_async(command)
