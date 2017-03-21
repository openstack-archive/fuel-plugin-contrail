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

@pytest.mark.xfail(run=False) #Remove when contrail-heat wil be added
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
    stack_params = heat_utils.read_params(template_file,
                                          predefined_contrail_params)
    (stack_name, ) = utils.generate_ids()
    create_stack(stack_name, template=template, parameters=stack_params)
