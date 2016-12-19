import pycontrail.client as client
import pytest
from six.moves.urllib import parse

from vapor import settings
from vapor.helpers.clients import ContrailClient


@pytest.yield_fixture
def client_contrail():
    with ContrailClient(settings.CONTRAIL_CREDS[
            'controller_addr']) as contrail:
        yield contrail
    print('helpers.clients.client_contrail')


@pytest.fixture
def contrail_nodes(os_faults_steps):
    """Returns all nodes which have contrail-status command."""
    return os_faults_steps.get_nodes_by_cmd('which contrail-status')


@pytest.fixture
def contrail_api_client(session):
    """Return instance of contail client."""
    neutron_endpoint = session.get_endpoint(service_type='network')
    parse_result = parse.urlparse(neutron_endpoint)
    contail_endpoint = parse_result._replace(netloc='{}:{}'.format(
        parse_result.hostname, settings.CONTAIL_API_PORT)).geturl()
    return client.Client(
        url=contail_endpoint, headers=session.get_auth_headers())
