# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from vapor import settings


def get_sriov_device_mapping(agent_steps):
    """Return computes with sriov neutron agents and them device mapping.

    Example output:
        {'node-4.test.domain.local': {"physnet2": ["ens11f1"]}}
    """
    agents = agent_steps.get_agents(binary=settings.NEUTRON_SRIOV_NIC_AGENT,
                                    check=False)
    mapping = {}
    for agent in agents:
        mapping[agent['host']] = agent['configurations']['device_mappings']
    return mapping


def get_sriov_numvfs(os_faults_steps, node, iface):
    """Return numvfs value from node for iface."""
    fqdn = os_faults_steps.get_fqdn_by_host_name(node)
    node = os_faults_steps.get_node(fqdns=[fqdn])
    cmd = 'cat /sys/class/net/{}/device/sriov_numvfs'.format(iface)
    result = os_faults_steps.execute_cmd(node, cmd)
    return int(result[0].payload['stdout'])
