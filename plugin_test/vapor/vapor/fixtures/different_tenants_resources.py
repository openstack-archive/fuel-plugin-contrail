# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import attrdict
import pytest
import six
import stepler.config as stepler_config
from stepler.third_party import utils

from vapor.helpers import project

if six.PY2:
    import contextlib2 as contextlib
else:
    import contextlib


class ResourceManager(object):
    def __init__(self, stack, base_name, get_network_steps, get_subnet_steps,
                 port_steps, get_floating_ip_steps, get_server_steps,
                 get_neutron_security_group_steps,
                 get_neutron_security_group_rule_steps, public_network):
        self.stack = stack
        self.base_name = base_name
        self.get_network_steps = get_network_steps
        self.get_subnet_steps = get_subnet_steps
        self.port_steps = port_steps
        self.get_floating_ip_steps = get_floating_ip_steps
        self.get_server_steps = get_server_steps
        self.get_neutron_security_group_steps = (
            get_neutron_security_group_steps)
        self.get_neutron_security_group_rule_steps = (
            get_neutron_security_group_rule_steps)
        self.public_network = public_network

    def _add_fin(self, steps_getter, fn_name, *args, **kwargs):
        def _fin():
            steps = steps_getter()
            fn = getattr(steps, fn_name)
            return fn(*args, **kwargs)

        return self.stack.callback(_fin)

    def _create_network(self):
        # Create network
        network = self.get_network_steps().create(self.base_name)
        self._add_fin(self.get_network_steps, 'delete', network)
        return network

    def _create_subnet(self, network, cidr):
        # Create subnet
        subnet = self.get_subnet_steps().create(self.base_name + '__subnet',
                                                network, cidr)
        self._add_fin(self.get_subnet_steps, 'delete', subnet)
        return subnet

    def _create_security_group(self):
        # Create security groups
        security_group_steps = self.get_neutron_security_group_steps()
        security_group = security_group_steps.create(self.base_name)
        self._add_fin(self.get_neutron_security_group_steps, 'delete',
                      security_group)
        self.get_neutron_security_group_rule_steps().add_rules_to_group(
            security_group['id'], stepler_config.SECURITY_GROUP_SSH_PING_RULES)
        return security_group

    def _create_server(self, image, flavor, nova_host, network, ip,
                       security_group):
        # Create server
        server_steps = self.get_server_steps()
        server = server_steps.create_servers(
            image=image,
            flavor=flavor,
            availability_zone='nova:{}'.format(nova_host),
            nics=[{
                'net-id': network['id'],
                'v4-fixed-ip': ip
            }],
            security_groups=[security_group],
            username=stepler_config.CIRROS_USERNAME,
            password=stepler_config.CIRROS_PASSWORD)[0]
        self._add_fin(self.get_server_steps, 'delete_servers', [server])
        return server

    def _add_floating_ip(self, port):
        # Add floating ip
        floating_ip = self.get_floating_ip_steps().create(self.public_network,
                                                          port)
        self._add_fin(self.get_floating_ip_steps, 'delete', floating_ip)
        return floating_ip

    def create(self, subnet_cidr, server_ip, image, flavor, nova_host):
        try:
            network = self._create_network()
            self._create_subnet(network, subnet_cidr)
            security_group = self._create_security_group()
            server = self._create_server(
                image=image,
                flavor=flavor,
                nova_host=nova_host,
                network=network,
                ip=server_ip,
                security_group=security_group)
            port = self.port_steps.get_port(
                device_owner=stepler_config.PORT_DEVICE_OWNER_SERVER,
                device_id=server.id)
            floating_ip = self._add_floating_ip(port)
        except Exception:
            self.stack.close()
            raise
        return attrdict.AttrDict({
            'server_steps': self.get_server_steps(),
            'network': network,
            'server': server,
            'port': port,
            'floating_ip': floating_ip,
            'security_group': security_group,
        })


@pytest.fixture
def project_2(create_user_with_project):
    """Fixture to create second admin project with user."""
    creds_alias = 'admin2'
    username = password = project_name = next(utils.generate_ids())
    with create_user_with_project(
            creds_alias,
            username=username,
            password=password,
            project_name=project_name,
            role_type=stepler_config.ROLE_ADMIN):
        yield creds_alias


@pytest.fixture
def different_tenants_resources(
        request, project_2, credentials, create_user_with_project,
        cirros_image, sorted_hypervisors, get_network_steps, get_subnet_steps,
        get_server_steps, port_steps, get_floating_ip_steps, public_flavor,
        public_network, get_neutron_security_group_steps,
        get_neutron_security_group_rule_steps, nova_availability_zone_hosts,
        get_current_project, contrail_api_client):
    """Fixture to create network, subnet and server on each of 2 projects.

    Created subnets has same CIDR.
    Created servers boot on same compute.

    Returns:
        list: list of AttrDict with created resources
    """
    default_params = {
        'subnet_cidr': '10.0.0.0/24',
        'base_name': next(utils.generate_ids()),
        'ips': (
            '10.0.0.11',
            '10.0.0.21', )
    }
    default_params.update(getattr(request, 'param', {}))

    subnet_cidr = default_params['subnet_cidr']
    base_name = default_params['base_name']
    ips = default_params['ips']

    hypervisor = sorted_hypervisors[0]

    host = next(
        host for host in nova_availability_zone_hosts
        if hypervisor.hypervisor_hostname.startswith(host))

    with contextlib.ExitStack() as stack:

        mrg = ResourceManager(
            stack, base_name, get_network_steps, get_subnet_steps, port_steps,
            get_floating_ip_steps, get_server_steps,
            get_neutron_security_group_steps,
            get_neutron_security_group_rule_steps, public_network)

        projects_resources = []

        project_resources = mrg.create(subnet_cidr, ips[0], cirros_image,
                                       public_flavor, host)

        contrail_project = project.get_contrail_project(get_current_project(),
                                                        contrail_api_client)
        project_resources.contrail_project = contrail_project
        projects_resources.append(project_resources)

        with credentials.change(project_2):

            project_resources = mrg.create(subnet_cidr, ips[1], cirros_image,
                                           public_flavor, host)
            contrail_project = project.get_contrail_project(
                get_current_project(), contrail_api_client)
            project_resources.contrail_project = contrail_project
            projects_resources.append(project_resources)
            yield projects_resources
