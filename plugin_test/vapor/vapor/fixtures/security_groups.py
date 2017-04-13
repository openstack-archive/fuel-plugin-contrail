# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import pycontrail.types as types
import pytest
from stepler.third_party import utils

from vapor import settings


@pytest.fixture
def contrail_security_groups_cleanup(contrail_api_client):
    """Cleanup created security_groups after test."""

    def _get_security_groups_uuids():
        return {
            security_group['uuid']
            for security_group in contrail_api_client.security_groups_list()[
                'security-groups']
        }

    before = _get_security_groups_uuids()

    yield

    for net_uuid in _get_security_groups_uuids() - before:
        contrail_api_client.security_group_delete(id=net_uuid)


@pytest.fixture
def create_contrail_security_group(contrail_api_client,
                                   contrail_security_groups_cleanup,
                                   contrail_current_project):
    """Callable fixture to create contrail security group."""

    def _create_sg(name=None):
        name = name or next(utils.generate_ids())
        security_group = types.SecurityGroup(
            name,
            security_group_entries=types.PolicyEntriesType(),
            parent_obj=contrail_current_project)
        contrail_api_client.security_group_create(security_group)
        return security_group

    return _create_sg


@pytest.fixture
def contrail_security_group(create_contrail_security_group):
    """Fixture to create contrail security group."""
    return create_contrail_security_group()


@pytest.fixture
def neutron_security_group(neutron_create_security_group,
                           neutron_security_group_rule_steps):
    """Function fixture to create security group before test.

    Can be called several times during test.
    After the test it destroys all created security groups

    Args:
        neutron_create_security_group (function): function to create security
            group with options
        neutron_security_group_rule_steps (object): instantiated security
            groups rules steps

    Returns:
        dict: security group
    """
    group_name = next(utils.generate_ids('security-group'))
    group = neutron_create_security_group(group_name)

    neutron_security_group_rule_steps.add_rules_to_group(
        group['id'], settings.SECURITY_GROUP_SSH_PING_RULES)

    return group
