# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import functools

import pycontrail.types as types
import pytest
from stepler import config as stepler_config
from stepler.third_party import utils

from vapor.helpers import service_chain


@pytest.fixture
def add_neutron_user_to_project(current_project, role_steps, user_steps):
    """Workaround to allow contrail to boot service instances."""
    neutron_user = user_steps.get_user(name='neutron')
    role = role_steps.get_role(name=stepler_config.ROLE_MEMBER)
    role_steps.grant_role(role, neutron_user, project=current_project)


@pytest.fixture
def service_template(contrail_api_client, nat_service_image, flavor):
    name = next(utils.generate_ids('nat_template'))
    interface_types = [
        types.ServiceTemplateInterfaceType(
            service_interface_type='management'),
        types.ServiceTemplateInterfaceType(service_interface_type='left'),
        types.ServiceTemplateInterfaceType(service_interface_type='right'),
    ]
    template_properties = types.ServiceTemplateType(
        version=1,
        service_mode=u'in-network',
        service_type=u'firewall',
        image_name=nat_service_image.name,
        flavor=flavor.name,
        interface_type=interface_types,
        ordered_interfaces=True,
        service_virtualization_type=u'virtual-machine')
    template = types.ServiceTemplate(
        name=name, service_template_properties=template_properties)
    contrail_api_client.service_template_create(template)
    yield template
    contrail_api_client.service_template_delete(id=template.uuid)


@pytest.fixture
def service_instance(request, contrail_api_client, contrail_current_project,
                     service_template, contrail_2_networks, server_steps,
                     add_neutron_user_to_project):
    left_vn, right_vn = contrail_2_networks.networks
    left_fq_name = ':'.join(left_vn['contrail:fq_name'])
    right_fq_name = ':'.join(right_vn['contrail:fq_name'])
    name = next(utils.generate_ids('nat_instance'))
    instance_properties = types.ServiceInstanceType(
        scale_out=types.ServiceScaleOutType(1),
        management_virtual_network='',
        left_virtual_network=left_fq_name,
        right_virtual_network=right_fq_name)
    instance = types.ServiceInstance(
        name=name,
        parent_obj=contrail_current_project,
        service_instance_properties=instance_properties)
    instance.set_service_template(service_template)
    contrail_api_client.service_instance_create(instance)

    request.addfinalizer(
        functools.partial(service_chain.delete_service_instance,
                          contrail_api_client, instance, server_steps))

    service_chain.check_service_instance_ready(contrail_api_client, instance,
                                               server_steps)
    return instance
