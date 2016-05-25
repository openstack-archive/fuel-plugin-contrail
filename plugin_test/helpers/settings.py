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

OSFT_RUN_TIMEOUT = 45 * 60  # 45 minutes
DEPLOY_CLUSTER_TIMEOUT = 25 * 60  # 25 minutes

BAREMETAL = {
    # Target Baremetal host
    'ipmi_user': os.environ.get('BM_IPMI_USER'),
    'ipmi_password': os.environ.get('BM_IPMI_PASSWORD'),
    'ipmi_host': os.environ.get('BM_IPMI_ADDR'),

    'target_mac': os.environ.get('BM_TARGET_MAC'),

    # Host where tests are running
    'host_ip': os.environ.get('BM_HOST_IP'),
    'host_bridge_interfaces': os.environ.get('BM_HOST_BRIDGE_INTERFACES'),
    'host_fuel_interfaces': os.environ.get('BM_HOST_FUEL_INTERFACES')
}
