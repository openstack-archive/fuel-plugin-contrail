# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from stepler.third_party import utils
import pytest

from vapor.helpers import heat_utils


def gen_id():
    return next(utils.generate_ids())


def get_fq_name(client, object_name):
    """Returns fq_name for 1'st contrail object from objects list."""
    methodname = '{}s_list'.format(object_name)
    method = getattr(client, methodname)
    obj = method(detail=True)[0]
    return ':'.join(obj.fq_name)


@pytest.mark.parametrize('template_file', heat_utils.list_templates())
def test_heat_templates(create_stack, template_file, contrail_current_project,
                        contrail_api_client):
    """Test create contrail-specific heat stack from template.

    Steps:
        #. Read stack template
        #. Read template variables from .env file
        #. Update template variables with contrail entities values
        #. Create heat stack
        #. Check that stack is reached 'COMPLETE' status
    """
    template = heat_utils.read_template(template_file)
    predefined_contrail_params = {
        'project': ":".join(contrail_current_project.fq_name),
        'domain': 'default-domain',
    }
    additional_keys = [
        'bgp_router',
        'floating_ip_pool',
        'global_system_config',
        'instance_ip',
        'namespace',
        'network_ipam',
        'network_policy',
        'route_table',
        'route_target',
        'routing_instance',
        'security_group',
        'service_appliance_set',
        'service_instance',
        'service_instance',
        'service_template',
        'virtual_machine',
        'virtual_machine_interface',
        'virtual_network',
        'virtual_router',
    ]
    for key in additional_keys:
        predefined_contrail_params[key] = get_fq_name(contrail_api_client, key)
    stack_params = heat_utils.read_params(template_file,
                                          predefined_contrail_params)
    (stack_name, ) = utils.generate_ids()
    create_stack(stack_name, template=template, parameters=stack_params)
