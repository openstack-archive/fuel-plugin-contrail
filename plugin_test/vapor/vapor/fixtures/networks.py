import pycontrail.types as types
import pytest
from stepler.third_party import utils


@pytest.fixture(autouse=True)
def network_cleanup(contrail_api_client):
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
        contrail_api_client.virtual_networks_delete(net_uuid)


@pytest.fixture
def network(contrail_api_client):
    network_name, = utils.generate_ids()
    net = types.VirtualNetwork(network_name)
    contrail_api_client.virtual_network_create(net)
    return net
