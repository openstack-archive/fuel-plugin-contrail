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


def activate(obj=None, vsrx_config=False,
             vsrx_ip='10.109.4.250', separate_net=False):
    """Activate vSRX1 image.

    :param obj: Test case object
    :param vsrx_ip: ip of vSRX router
    :param vsrx_config: upload vsrx configuration template
    :param separate_net: create network for vSRX router

    """
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

    if separate_net:
        commands = [
            'virsh net-create {0}'.format(settings.LIBVIRT_NET_PATH),
            'sed -i -r "s/qa_private/vsrx_internal_net/g" logs/vSRX1.xml',
            'sed -i -r "s/vSRX.400.img/vSRX_gateway.img/g" logs/vSRX1.xml'
        ]
        map(call_cmd, commands)

    logger.info("#" * 10 + 'Create vSRX...' + "#" * 10)
    if subprocess.call('virsh create logs/vSRX1.xml', shell=True):
        logger.info("#" * 10 + 'VSRX could not be established, '
                    'OSTF will not be running' + "#" * 10)
        return False

    map(call_cmd, [
        'sudo ip route del 10.100.1.0/24',
        'sudo ip route add 10.100.1.0/24 via 10.109.3.250'])

    if vsrx_config and settings.VSRX_CONFIG_PATH:
        assert obj, "obj is None"
        upload_config(obj, settings.VSRX_CONFIG_PATH, vsrx_ip)
    return True


def upload_config(obj, config_path, vsrx_ip):
    """Upload and commit configuration for VSRX."""
    commands = [
        'cli', 'configure',
        'load override {0}'.format(config_path.split('/').pop()),
        'commit'
        ]
    wait(
        lambda: tcp_ping(vsrx_ip, 22), timeout=60 * 2, interval=10,
        timeout_msg="Node {0} is not accessible by SSH.".format(vsrx_ip))
    with obj.env.d_env.get_ssh_to_remote(vsrx_ip) as remote:
        logger.info('Upload template {0}'.format(config_path))
        remote.upload(config_path, '/cf/root')
        for command in commands:
            logger.info('Execute command {0}.'.format(command))
            remote.execute_async(command)

