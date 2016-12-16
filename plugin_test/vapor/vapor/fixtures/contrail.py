import pytest

from vapor.settings import CONTRAIL_CREDS
from vapor.helpers.clients import ContrailClient


@pytest.yield_fixture
def client_contrail():
    with ContrailClient(CONTRAIL_CREDS['controller_addr']) as contrail:
        yield contrail
    print('helpers.clients.client_contrail')


@pytest.fixture
def contrail_nodes(os_faults_steps):
    """Returns all nodes which have contrail-status command."""
    return os_faults_steps.get_nodes_by_cmd('contrail-status')
