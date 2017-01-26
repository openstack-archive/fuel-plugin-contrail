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

VSRX_TEMPLATE_PATH = os.environ.get('VSRX_TEMPLATE_PATH', False)
LIBVIRT_NET_PATH = os.environ.get('LIBVIRT_NET_PATH', False)

OSTF_RUN_TIMEOUT = 60 * 60  # 60 minutes
DEPLOY_CLUSTER_TIMEOUT = 25 * 60  # 25 minutes
CONTRAIL_PLUGIN_VERSION = os.environ.get('CONTRAIL_PLUGIN_VERSION', '5.0.0')
VSRX_CONFIG_PATH = os.environ.get(
    'VSRX_CONFIG_PATH', '/storage/contrail/config_2nodegroups.conf')

VSRX_USER = os.environ.get('VSRX_USER', False)
VSRX_PASS = os.environ.get('VSRX_PASS', False)

NEW_CONTRAIL_PLUGIN_PATH = os.environ.get('NEW_CONTRAIL_PLUGIN_PATH')
NEW_CONTRAIL_PLUGIN_VERSION = os.environ.get(
    'NEW_CONTRAIL_PLUGIN_VERSION', '5.0.1')

BAREMETAL = {
    # Target Baremetal host
    'ipmi_user': os.environ.get('BM_IPMI_USER'),
    'ipmi_password': os.environ.get('BM_IPMI_PASSWORD'),
    'ipmi_host': os.environ.get('BM_IPMI_ADDR'),

    # Host where tests are running
    # format: "mac1;mac2"
    'target_macs': os.environ.get('BM_TARGET_MACS'),
    # format: "interface:subnet;interface:subnet"
    # i.e.: "eth1:127.0.0.1/24;eth2:192.168.0.1/24"
    'host_bridge_interfaces': os.environ.get('BM_HOST_BRIDGE_INTERFACES'),
}

UPDATE_PLUGIN = os.environ.get('UPDATE_PLUGIN', False)
