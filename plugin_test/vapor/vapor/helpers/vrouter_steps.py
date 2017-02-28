# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from vapor.helpers import nodes_steps


def get_route_table(os_faults_steps, nodes):
    """Return route tables for each node."""
    result = os_faults_steps.execute_cmd(nodes, 'ip r')
    tables = {}
    for node_result in result:
        node = nodes_steps.get_node_by_result(node_result, os_faults_steps)
        tables[node.fqdn] = node_result.payload['stdout_lines']
    return tables
