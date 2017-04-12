# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from stepler import config as stepler_config

from vapor.helpers import nodes_steps


def get_sriov_devices(os_faults_steps, computes):
    """Return computes with sriov neutron agents and them ifaces data.

    Example output:
        {'node-4.test.domain.local': {"ens11f1": {"sriov_numvfs": 7}}}
    """
    cmd = "grep -v 0 /sys/class/net/*/device/sriov_numvfs"
    result = os_faults_steps.execute_cmd(computes, cmd, check=False)
    mapping = {}
    for node_result in result:
        node = nodes_steps.get_node_by_result(node_result, os_faults_steps)
        if node_result.status == stepler_config.STATUS_OK:
            node_data = {}
            for line in node_result.payload['stdout_lines']:
                path, sriov_numvfs = line.split(':')
                sriov_numvfs = int(sriov_numvfs)
                iface = path.split('/')[4]
                node_data[iface] = {'sriov_numvfs': sriov_numvfs}
            mapping[node.fqdn] = node_data

    return mapping
