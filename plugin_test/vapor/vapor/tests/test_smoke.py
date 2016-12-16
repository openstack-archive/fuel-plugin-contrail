# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from hamcrest import assert_that, empty


def test_contrail_node_services_status(contrail_nodes, os_faults_steps):
    cmd = "contrail-status | grep -Pv '(==|^$)'"
    broken_services = []
    for node_result in os_faults_steps.execute_cmd(contrail_nodes, cmd):
        for line in node_result.payload['stdout_lines']:
            line = line.strip()
            name, status = line.split(None, 1)
            if status not in {'active', 'backup'}:
                err_msg = "{node}:{service} - {status}".format(
                    node=node_result.host, service=name, status=status)
                broken_services.append(err_msg)
    assert_that(broken_services, empty())
