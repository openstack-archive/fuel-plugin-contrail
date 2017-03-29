from pycontrail import exceptions
import pycontrail.types as types
import pytest
from stepler.third_party import utils


@pytest.fixture
def contrail_policies_cleanup(contrail_api_client):
    """Cleanup created policies after test."""

    def _get_policies_uuids():
        return {
            policy['uuid']
            for policy in contrail_api_client.network_policys_list()[
                'network-policys']
        }

    before = _get_policies_uuids()

    yield

    for net_uuid in _get_policies_uuids() - before:
        contrail_api_client.network_policy_delete(id=net_uuid)


@pytest.fixture
def create_network_policy(contrail_api_client, contrail_current_project):
    """Fixture to create network policy."""

    policies = []

    def _create_network_policy(name=None, parent=None):
        name = name or next(utils.generate_ids())
        parent = parent or contrail_current_project
        policy = types.NetworkPolicy(name, parent_obj=parent)
        contrail_api_client.network_policy_create(policy)

        policies.append(policy)

        return policy

    yield _create_network_policy

    for policy in policies:
        try:
            policy = contrail_api_client.network_policy_read(id=policy.uuid)
        except exceptions.NoIdError:
            continue
        contrail_api_client.network_policy_delete(id=policy.uuid)


@pytest.fixture
def contrail_network_policy(create_network_policy):
    return create_network_policy()
