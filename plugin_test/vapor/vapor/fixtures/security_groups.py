import pycontrail.types as types
import pytest
from stepler.third_party import utils


@pytest.fixture(autouse=True)
def security_groups_cleanup(contrail_api_client):
    """Cleanup created networks after test."""
    def _get_sg_uuids():
        return {
            net['uuid']
            for net in contrail_api_client.security_groups_list()[
                'security-groups']
        }

    before = _get_sg_uuids()

    yield

    for net_uuid in _get_sg_uuids() - before:
        contrail_api_client.security_group_delete(id=net_uuid)


@pytest.fixture
def security_group(contrail_api_client):
    security_group_name, = utils.generate_ids()
    security_group = types.SecurityGroup(security_group_name)
    contrail_api_client.security_group_create(security_group)
    return security_group
