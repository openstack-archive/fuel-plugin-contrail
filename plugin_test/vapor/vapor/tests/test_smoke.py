import pytest

from vapor.helpers.clients.contrail_api import ContrailClient
from vapor.settings import CONTRAIL_CREDS

from stepler.keystone.fixtures import keystone_client, get_keystone_client

@pytest.mark.parametrize("contrail_node_role", [
    'contrail-controller',
    'contrail-analytics',
    'contrail-analytics-db'
])
@pytest.mark.idempotent_id('1b1a0953-a772-4cfe-a7da-2f6de950123')
def test_contrail_node_exist(keystone_client, contrail_node_role):
    services = []
    for service in keystone_client.services.list():
        services.append(service.name)
    print('Check contrail node %s status' % contrail_node_role)
    assert contrail_node_role in services


def test_contrail_node_status(keytone_client):
