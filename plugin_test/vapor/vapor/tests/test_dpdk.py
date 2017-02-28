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
                      is_not, empty, greater_than, has_length)

from vapor.helpers import contrail_status
from vapor.helpers import dpdk
from vapor.helpers import nodes_steps
from vapor.helpers import vrouter_steps
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


def test_bound_network_interfaces(os_faults_steps, computes):
    """Verify if DPDK vRouter binds network interfaces."""
    devices = dpdk.get_devices(os_faults_steps, computes)
    assert_that(devices.values(),
                only_contains(
                    has_entries('Network devices using DPDK-compatible driver',
                                is_not(empty()))))


def test_huge_pages_usage(os_faults_steps, computes):
    """Verify if vRrouter uses Huge Pages."""
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


def test_contrail_vrouter_dpdk_cpu_usage(os_faults_steps, computes):
    """Verify if vRouter uses CPU."""
    cmd = "ps -c contrail-vrouter-dpdk -o %cpu="
    result = os_faults_steps.execute_cmd(computes, cmd)
    for node_result in result:
        usage = node_result.payload['stdout']
        usage = float(usage.strip())
        assert_that(usage, greater_than(50))


def test_vrouter_create_interface(request, os_faults_steps, computes):
    """Verify if vRouter creates interface after creation of a virtual machine.

    Steps:
        #. Remember count of virtual interfaces on vRouters
        #. Create server
        #. Check that count of virtual interfaces on server's compute vRouter
            is greater than it was.
    """
    before_ifaces = vrouter_steps.get_interface_table(os_faults_steps,
                                                      computes)
    server = request.getfixturevalue('server')
    compute_fqdn = getattr(server, settings.SERVER_ATTR_HYPERVISOR_HOSTNAME)
    after_ifaces = vrouter_steps.get_interface_table(os_faults_steps, computes)
    assert_that(after_ifaces[compute_fqdn],
                has_length(greater_than(len(before_ifaces[compute_fqdn]))))
