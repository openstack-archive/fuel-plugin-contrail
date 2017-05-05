# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import pytest
from stepler.glance.fixtures import images
from stepler.third_party import utils

from vapor import settings


@pytest.fixture(scope='session')
def nat_service_image(get_glance_steps, uncleanable, credentials):
    """Session fixture to create ubuntu image.
    Creates image from config.UBUNTU_QCOW2_URL with default options.

    Args:
        get_glance_steps (function): function to get glance steps
        uncleanable (AttrDict): data structure with skipped resources
        credentials (object): CredentialsManager instance

    Returns:
        object: ubuntu glance image
    """
    with images.create_images_context(
            get_glance_steps,
            uncleanable,
            credentials,
            utils.generate_ids('nat'),
            settings.NAT_SERVICE_IMAGE_URL) as created_images:
        yield created_images[0]
