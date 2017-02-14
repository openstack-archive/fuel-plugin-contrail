from pycontrail import exceptions
import pycontrail.types as types
import pytest
from stepler.third_party import utils


@pytest.fixture
def contrail_network_cleanup(contrail_api_client):
    """Cleanup created networks after test."""

    def _get_networks_uuids():
        return {
            net['uuid']
            for net in contrail_api_client.virtual_networks_list()[
                'virtual-networks']
        }

    before = _get_networks_uuids()

    yield

    for net_uuid in _get_networks_uuids() - before:
        contrail_api_client.virtual_network_delete(id=net_uuid)


@pytest.fixture
def neutron_network_cleanup(network_steps):
    def _get_network_id():
        return {net['id'] for net in network_steps.get_networks(check=False)}

    before = _get_network_id()

    yield

    for net_id in _get_network_id() - before:
        network_steps.delete({'id': net_id})


@pytest.fixture
def create_contrail_network(contrail_api_client, contrail_current_project):
    """Callable fixture to create contrail network."""

    networks = []

    def _create_network(name=None, parent_obj=None, **kwargs):
        if name is None:
            name, = utils.generate_ids()
        parent_obj = parent_obj or contrail_current_project
        net = types.VirtualNetwork(name, parent_obj=contrail_current_project,
                                   **kwargs)
        contrail_api_client.virtual_network_create(net)
        return net

    yield _create_network

    for net in reversed(networks):
        try:
            contrail_api_client.virtual_network_delete(id=net.uuid)
        except exceptions.NoIdError:
            pass


@pytest.fixture
def contrail_network(create_contrail_network):
    return create_contrail_network()


@pytest.fixture
def set_network_policy(contrail_api_client):

    networks = []

    def _set_network_policy(network, policy):
        networks.append((network, policy))
        policy_type = types.VirtualNetworkPolicyType(
            sequence={'major': 0,
                      'minor': 0})
        network.add_network_policy(policy, policy_type)
        contrail_api_client.virtual_network_update(network)

    yield _set_network_policy

    for network, policy in reversed(networks):
        network.del_network_policy(policy)
        contrail_api_client.virtual_network_update(network)
