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

import os
import time
import subprocess

from fuelweb_test import logger
from fuelweb_test.helpers import checkers
from fuelweb_test.settings import CONTRAIL_PLUGIN_PATH
from proboscis.asserts import assert_true
from settings import VSRX_TEMPLATE_PATH
from settings import CONTRAIL_PLUGIN_VERSION
import openstack


BOND_CONFIG = [
    {
        'mac': None,
        'mode': 'balance-rr',
        'name': 'lnx-bond0',
        'slaves': [
            {'name': 'enp0s6'},
            {'name': 'enp0s7'},
        ],
        'state': None,
        'type': 'bond',
        'assigned_networks': []
    }
]

INTERFACES = {
    'enp0s3': ['fuelweb_admin', 'storage'],
    'enp0s4': ['public'],
    'enp0s5': ['management'],
    'lnx-bond0': ['private']
}


def upload_contrail_packages(obj):
    """Upload contrail packeges on master node."""
    node_ssh = obj.env.d_env.get_admin_remote()
    if os.path.splitext(obj.pack_path)[1] == ".deb":
        pkg_name = os.path.basename(obj.pack_path)
        logger.debug("Uploading package {0} "
                     "to master node".format(pkg_name))
        node_ssh.upload(obj.pack_path, obj.pack_copy_path)
    else:
        raise Exception('Failed to upload file to the master node')


def install_packages(obj, remote):
    """Install contrail packeges on master node."""
    command = "cd " + obj.pack_copy_path + " && ./install.sh"
    logger.info('The command is %s', command)
    remote.execute_async(command)
    time.sleep(50)
    os.path.isfile(obj.add_package)


def prepare_contrail_plugin(obj, slaves=None, options={}):
    """Copy necessary packages to the master node and install them."""
    obj.env.revert_snapshot("ready_with_%d_slaves" % slaves)

    # copy plugin to the master node
    checkers.upload_tarball(
        obj.env.d_env.get_admin_remote(),
        CONTRAIL_PLUGIN_PATH, '/var')

    # install plugin
    checkers.install_plugin_check_code(
        obj.env.d_env.get_admin_remote(),
        plugin=os.path.basename(CONTRAIL_PLUGIN_PATH))
    # FIXME: when opencontrail v3.0 is available
    # FIXME: remove the following line from 'or True'
    if obj.CONTRAIL_DISTRIBUTION == 'juniper' or True:
        # copy additional packages to the master node
        upload_contrail_packages(obj)

        # install packages
        install_packages(obj, obj.env.d_env.get_admin_remote())

    # prepare fuel
    openstack.assign_net_provider(obj, **options)


def activate_plugin(obj, **kwargs):
    """Enable plugin in contrail settings."""
    plugin_name = 'contrail'
    msg = "Plugin couldn't be enabled. Check plugin version. Test aborted"
    assert_true(
        obj.fuel_web.check_plugin_exists(obj.cluster_id, plugin_name),
        msg)
    logger.debug('we have contrail element')

    options = {}
    if kwargs:
        for option in kwargs:
            options.update(
                {'{0}/value'.format(option): kwargs[option]})

    obj.fuel_web.update_plugin_settings(
        obj.cluster_id, plugin_name, CONTRAIL_PLUGIN_VERSION, options)


def activate_vsrx():
    """Activate vSRX1 image."""
    logger.info("#" * 10 + 'Configure iptables and route...' + "#" * 10)
    command = 'sudo /sbin/iptables -F'
    logger.info('The command is %s', command)
    subprocess.call(command, shell=True)
    command = 'sudo /sbin/iptables -t nat -F'
    logger.info('The command is %s', command)
    subprocess.call(command, shell=True)
    command = 'sudo /sbin/iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE'
    logger.info('The command is %s', command)
    subprocess.call(command, shell=True)

    if not VSRX_TEMPLATE_PATH:
        logger.info("#" * 10 + 'VSRX_TEMPLATE_PATH is not defined, '
                    'OSTF will not be running' + "#" * 10)
        return False

    logger.info(
        "#" * 10 + 'Delete previous installation of vSRX...' + "#" * 10)
    command = 'virsh destroy vSRX1'
    logger.info('The command is %s', command)
    subprocess.call(command, shell=True)
    command = 'virsh undefine vSRX1'
    logger.info('The command is %s', command)
    subprocess.call(command, shell=True)
    command = 'sed -r "s/ENV_NAME/$ENV_NAME/g" {0} > logs/vSRX1.xml'.\
        format(VSRX_TEMPLATE_PATH)
    logger.info('The command is %s', command)
    subprocess.call(command, shell=True)
    command = 'sed -i -r "s/vSRX1.img/vSRX.400.img/g" logs/vSRX1.xml'
    logger.info('The command is %s', command)
    subprocess.call(command, shell=True)
    command = 'virsh create logs/vSRX1.xml'
    logger.info("#" * 10 + 'Create vSRX...' + "#" * 10)
    if subprocess.call(command, shell=True):
        logger.info("#" * 10 + 'VSRX could not be established, '
                    'OSTF will not be running' + "#" * 10)
        return False
    command = 'sudo ip route del 10.100.1.0/24'
    logger.info('The command is %s', command)
    subprocess.call(command, shell=True)
    command = 'sudo ip route add 10.100.1.0/24 via 10.109.3.250'
    logger.info('The command is %s', command)
    subprocess.call(command, shell=True)
    return True


def net_group_preparation(obj):
    """Prepare network group for network template."""
    node_ssh = obj.env.d_env.get_admin_remote()
    net_name = 'private'
    command = 'fuel network-group --env {0} | grep {1}'.format(
        obj.cluster_id, net_name)
    # get private net params
    output = node_ssh.execute(command)['stdout'].pop()
    ids, name, vlan_start, cidr, gateway, group_id = [
        x.strip() for x in output.split('|')]
    gateway = cidr.split('0/').pop(0) + '1'
    # preparing commands for gateway setting and  private interface updating
    logger.info('{0} {1} {2}'.format(ids, net_name, cidr))
    commands = [
        'fuel network-group --set --network %s --gateway %s' % (ids, gateway),
        """fuel network-group --set --network %s --meta \'
           {"name": %s, "notation": "cidr",
           "render_type": null, "map_priority": 2, "configurable": true,
            "render_addr_mask": "internal", "vlan_start": null,
            "use_gateway": true, "cidr": %s}\'""" % (ids, net_name, cidr)]

    for i in commands:
        node_ssh.execute_async(i)
        time.sleep(40)


def show_range(obj, start_value, end_value):
    """Show several steps."""
    for i in range(start_value, end_value):
        obj.show_step(i)


def change_contrail_api_port(obj, port):
    """Change port of Contrail API.

    :param value: type string, port number.
    """
    clatts = obj.fuel_web.client.get_cluster_attributes(obj.cluster_id)
    clatts['editable']['contrail']['metadata']['versions'][0][
        'contrail_api_public_port']['value'] = port
    obj.fuel_web.client.update_cluster_attributes(obj.cluster_id, clatts)
    clatts = obj.fuel_web.client.get_cluster_attributes(obj.cluster_id)
    assert_true(
        clatts['editable']['contrail']['metadata']['versions'][0][
            'contrail_api_public_port']['value'] == port,
        "Contrail api port is not equal {0}".format(port))


def activate_dpdk(obj):
    """Activate DPDK functionality"""
    clatts = obj.fuel_web.client.get_cluster_attributes(obj.cluster_id)
    clatts['editable']['contrail']['metadata']['versions'][0]['contrail_global_dpdk']['value'] = True
    clatts['editable']['contrail']['metadata']['versions'][0]['hugepages_amount']['value'] = 50
    obj.fuel_web.client.update_cluster_attributes(obj.cluster_id, clatts)

