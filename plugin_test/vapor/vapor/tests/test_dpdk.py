# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from hamcrest import (assert_that, has_entries, has_item, only_contains,
                      is_not, empty)

from vapor.helpers import contrail_status
from vapor.helpers import dpdk
from vapor.helpers import nodes_steps
from vapor import settings


def test_contrail_vrouter_dpdk(os_faults_steps):
    """Validate existence and status for contrail-vrouter-dpdk service."""
    statuses = contrail_status.get_services_statuses(os_faults_steps)
    for fqdn in settings.CONTRAIL_ROLES_DISTRIBUTION[
            settings.ROLE_CONTRAIL_COMPUTE]:
        compute_services = statuses[fqdn]
        assert_that(
            compute_services,
            has_item(
                has_entries(name='contrail-vrouter-dpdk', status='active')))


def test_bound_network_interfaces(os_faults_steps):
    """Verify if DPDK vRouter binds network interfaces."""
    fqdns = settings.CONTRAIL_ROLES_DISTRIBUTION[
        settings.ROLE_CONTRAIL_COMPUTE]
    computes = os_faults_steps.get_nodes(fqdns)
    devices = dpdk.get_devices(os_faults_steps, computes)
    assert_that(devices.values(),
                only_contains(
                    has_entries('Network devices using DPDK-compatible driver',
                                is_not(empty()))))


def test_huge_pages_usage(os_faults_steps):
    """Verify if vRrouter uses Huge Pages."""
    fqdns = settings.CONTRAIL_ROLES_DISTRIBUTION[
        settings.ROLE_CONTRAIL_COMPUTE]
    computes = os_faults_steps.get_nodes(fqdns)
    result = os_faults_steps.execute_cmd(computes, 'grep Huge /proc/meminfo')
    for node_result in result:
        node = nodes_steps.get_node_by_result(node_result, os_faults_steps)
        data = {}
        for line in node_result.payload['stdout_lines']:
            key, value = line.split(':', 1)
            data[key] = value.strip()
        assert_that(data,
                    has_entries(
                        HugePages_Total=is_not('0'), AnonHugePages='0 kB'),
                    node.fqdn)
