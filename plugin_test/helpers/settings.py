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

OSTF_RUN_TIMEOUT = 45 * 60  # 45 minutes
DEPLOY_CLUSTER_TIMEOUT = 25 * 60  # 25 minutes
CONTRAIL_PLUGIN_VERSION = os.environ.get('CONTRAIL_PLUGIN_VERSION', '4.0.0')

BAREMETAL_IMPI = {
    'user': os.environ.get('BM_IPMI_USER'),
    'password': os.environ.get('BM_IPMI_PASSWORD'),
    'host': os.environ.get('BM_IPMI_HOST'),
    'remote_ip': os.environ.get('BM_IP'),
}
