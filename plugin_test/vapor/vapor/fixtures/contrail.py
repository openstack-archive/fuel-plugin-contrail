import pytest

from vapor.settings import CONTRAIL_CREDS
from vapor.helpers.clients import ContrailClient


@pytest.yield_fixture
def client_contrail():
    with ContrailClient(CONTRAIL_CREDS['controller_addr']) as contrail:
        yield contrail
    print('helpers.clients.client_contrail')
