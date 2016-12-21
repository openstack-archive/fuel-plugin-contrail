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
def contrail_network_policy(contrail_api_client):
    policy_name, = utils.generate_ids()
    policy = types.NetworkPolicy(policy_name)
    contrail_api_client.network_policy_create(policy)
    return policy
