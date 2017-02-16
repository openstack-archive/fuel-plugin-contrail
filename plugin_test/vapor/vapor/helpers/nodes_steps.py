# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.


def get_nodes_interfaces(os_faults_steps, nodes=None):
    """Return dict with all nodes interfaces names."""
    nodes = nodes or os_faults_steps.get_nodes()
    results = os_faults_steps.execute_cmd(nodes, "ip -o a | awk '{print $2}'")
    ifaces = {}
    for node_result in results:
        node = next(node for node in nodes if node.ip == node_result.host)
        ifaces[node.fqdn] = set(node_result.payload['stdout_lines'])
    return ifaces
