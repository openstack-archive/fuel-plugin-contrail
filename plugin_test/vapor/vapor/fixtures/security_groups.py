import pycontrail.types as types
import pytest
from stepler.third_party import utils


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
def contrail_security_group(contrail_api_client):
    security_group_name, = utils.generate_ids()
    security_group = types.SecurityGroup(security_group_name)
    contrail_api_client.security_group_create(security_group)
    return security_group
