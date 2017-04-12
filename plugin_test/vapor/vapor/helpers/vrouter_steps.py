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


def get_interface_table(os_faults_steps, nodes):
    """Return interface table for each node.

    Format:
    {u'node-5.test.domain.local': [
        {'name': u'vif0/3',
         u'HWaddr': u'00:00:5e:00:01:00',
         u'Flags': u'PL3L2D',
         ....},
         {.....}
    ]}
    """
    cmd = "vif --list"
    result = os_faults_steps.execute_cmd(nodes, cmd)
    tables = {}
    for node_result in result:
        node = nodes_steps.get_node_by_result(node_result, os_faults_steps)
        table = []
        iface = {}
        for line in node_result.payload['stdout_lines']:
            if not line.strip():
                if iface:
                    table.append(iface)
                    iface = {}
            else:
                if ':' not in line or line.startswith('Flags:'):
                    continue
                elif line[0] != ' ':
                    name, key, value = line.split(None, 2)
                    key = key.strip(':')
                    iface['name'] = name
                    pairs = {key: value}
                else:
                    pairs = line.split()
                    start = next(i for i, pair in enumerate(pairs)
                                 if ':' in pair)
                    prefix = u'_'.join(pairs[:start])
                    pairs = [
                        u'{}_{}'.format(prefix, p) for p in pairs[start:]
                    ]
                    pairs = dict(x.split(':', 1) for x in pairs)
                iface.update(pairs)
        if iface:
            table.append(iface)
        tables[node.fqdn] = table
    return tables
