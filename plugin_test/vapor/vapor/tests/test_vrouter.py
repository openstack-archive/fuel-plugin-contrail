# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import uuid

from hamcrest import assert_that, equal_to
import pycontrail.types as types
import pytest
from stepler import config as stepler_config

from vapor.helpers import vrouter_steps


@pytest.mark.requires('computes_count >= 2')
def test_router_table_cleanup(cirros_image, flavor, network, subnet,
                              current_project, server_steps,
                              sorted_hypervisors, port_steps, os_faults_steps,
                              contrail_api_client, iface_route_table_create):
    """Check that added routes are cleaned up after servers to be deleted."""
    hypervisor1, hypervisor2 = sorted_hypervisors[:2]
    hypervisor1, = sorted_hypervisors[:1]
    server_create_args = dict(
        image=cirros_image, flavor=flavor, networks=[network])
    computes = os_faults_steps.get_nodes(fqdns=[
        hypervisor1.hypervisor_hostname, hypervisor2.hypervisor_hostname
    ])

    route_table_before = vrouter_steps.get_route_table(os_faults_steps,
                                                       computes)

    server1 = server_steps.create_servers(
        availability_zone='nova:' + hypervisor1.hypervisor_hostname,
        **server_create_args)[0]
    server2 = server_steps.create_servers(
        availability_zone='nova:' + hypervisor2.hypervisor_hostname,
        **server_create_args)[0]
    port = port_steps.get_port(
        device_owner=stepler_config.PORT_DEVICE_OWNER_SERVER,
        device_id=server1.id)

    project_id = str(uuid.UUID(current_project.id))
    project = contrail_api_client.project_read(id=project_id)
    iface = contrail_api_client.virtual_machine_interface_read(id=port['id'])

    route = types.RouteType(
        prefix='0.0.0.0/0', next_hop=server_steps.get_fixed_ip(server2))
    route_table = types.RouteTableType(route=[route])

    iface_route_table = types.InterfaceRouteTable(
        name="test3",
        parent_obj=project,
        interface_route_table_routes=route_table)
    iface_route_table_create(iface_route_table)
    iface.add_interface_route_table(iface_route_table)
    contrail_api_client.virtual_machine_interface_update(iface)

    server_steps.delete_servers([server1, server2])

    route_table_after = vrouter_steps.get_route_table(os_faults_steps,
                                                      computes)
    assert_that(route_table_after, equal_to(route_table_before))
