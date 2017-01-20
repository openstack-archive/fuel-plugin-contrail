from pycontrail import exceptions
import pycontrail.types as types
import pytest
from stepler.third_party import utils


@pytest.fixture
def contrail_policies_cleanup(contrail_api_client):
    """Cleanup created policies after test."""

    def _get_policies_uuids():
        return {
            net['uuid']
            for net in contrail_api_client.network_policys_list()[
                'network-policys']
        }

    before = _get_policies_uuids()

    yield

    for net_uuid in _get_policies_uuids() - before:
        contrail_api_client.network_policy_delete(id=net_uuid)


@pytest.fixture
def contrail_network_policy(contrail_api_client, contrail_current_project):
    policy_name, = utils.generate_ids()
    policy = types.NetworkPolicy(
        policy_name, parent_obj=contrail_current_project)
    contrail_api_client.network_policy_create(policy)

    yield policy

    try:
        contrail_api_client.network_policy_delete(id=policy.uuid)
    except exceptions.NoIdError:
        pass
