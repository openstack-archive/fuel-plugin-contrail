# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import os
import uuid

import yaml

from vapor import settings


def _randomize(data):
    for k, v in data.items():
        if v == 'Something':
            data[k] += uuid.uuid4().hex[:4]
    return data


def list_templates():
    """Returns list of yaml file from template folder."""
    files = os.listdir(os.path.join(settings.HEAT_TEMPLATES_PATH, 'template'))
    return [f for f in files if f.endswith('.yaml')]


def read_params(template_name, values):
    """Returns dict with template parameters from .evn file."""
    name = template_name.split('.')[0]
    path = os.path.join(settings.HEAT_TEMPLATES_PATH, 'template',
                        name + '.env')
    with open(path) as f:
        data = f.read()
        data = data.format(**values)
        data = yaml.safe_load(data)['parameters']
        return _randomize(data)


def read_template(template_name):
    """Returns content of .yaml template."""
    path = os.path.join(settings.HEAT_TEMPLATES_PATH, 'template',
                        template_name)
    with open(path) as f:
        return f.read()
