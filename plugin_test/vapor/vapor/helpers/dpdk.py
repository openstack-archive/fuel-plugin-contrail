# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.


import itertools

from stepler import config as stepler_config

from vapor.helpers import nodes_steps


def get_devices(os_faults_steps, nodes):
    result = os_faults_steps.execute_cmd(
        nodes, 'dpdk_nic_bind --status', check=False)
    node_statuses = {}
    for node_result in result:
        node = nodes_steps.get_node_by_result(node_result, os_faults_steps)
        statuses = {}
        if node_result.status == stepler_config.STATUS_OK:
            lines = node_result.payload['stdout_lines']
            for empty, section in itertools.groupby(
                    lines, key=lambda x: x.strip() == ''):
                if empty:
                    continue
                section = tuple(section)
                name = section[0]
                ifaces = [x for x in section[2:] if x.strip() != '<none>']
                statuses[name] = ifaces
        node_statuses[node.fqdn] = statuses
    return node_statuses
