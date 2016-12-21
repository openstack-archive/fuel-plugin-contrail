import pycontrail.client as client
import pytest

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
def contrail_controllers(os_faults_steps, contrail_nodes):
    """Returns all contrail controller nodes."""
    return os_faults_steps.get_nodes_by_cmd(
        'contrail-status | grep -v "Contrail vRouter"')


@pytest.fixture(scope='module')
def contrail_api_endpoint(os_faults_steps):
    """Return contrail api endpoint."""
    config_path = settings.NEUTRON_CONTRAIL_PLUGIN_CONFIG_PATH
    contrail_node = os_faults_steps.get_nodes_by_cmd(
        'grep -P "^\s*api_server_ip" {}'.format(config_path)).pick()
    awk_cmd = r"awk -F '=' '/^\s*{key}/ {{ print $2 }}' {path}"
    ip = os_faults_steps.execute_cmd(
        contrail_node, awk_cmd.format(
            key='api_server_ip', path=config_path))[0].payload['stdout']
    port = os_faults_steps.execute_cmd(
        contrail_node, awk_cmd.format(
            key='api_server_port', path=config_path))[0].payload['stdout']
    return 'http://{}:{}/'.format(ip.strip(), port.strip())


@pytest.fixture
def contrail_api_client(session, contrail_api_endpoint):
    """Return instance of contail client."""
    headers = {'Content-type': 'application/json; charset="UTF-8"'}
    headers.update(session.get_auth_headers())
    return client.Client(
        url=contrail_api_endpoint, headers=headers, blocking=False)
