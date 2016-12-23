import pycontrail.client as client
import pytest
from six.moves.urllib import parse

from vapor import settings
from vapor.helpers import clients


@pytest.fixture
def client_contrail(session, contrail_api_endpoint):
    with clients.ContrailClient(session, contrail_api_endpoint) as contrail:
        yield contrail


@pytest.fixture
def client_contrail_analytics(session, contrail_analytics_endpoint):
    return clients.ContrailAnalyticsClient(session,
                                           contrail_analytics_endpoint)


def get_nodes_fixture(cmd):
    """Fixtures to gen nodes by cmd factory."""

    @pytest.fixture
    def nodes_fixture(os_faults_steps):
        return os_faults_steps.get_nodes_by_cmd(cmd)

    return nodes_fixture


contrail_nodes = get_nodes_fixture('contrail-status | grep .')
contrail_controllers = get_nodes_fixture(
    'contrail-status | grep "Contrail Control"')
contrail_db_nodes = get_nodes_fixture(
    "contrail-status | grep -P "
    "'(Contrail Database|Contrail Supervisor Database)'")

contrail_analytics_nodes = get_nodes_fixture(
    "contrail-status | grep 'Contrail Analytics'")


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


@pytest.fixture(scope='module')
def contrail_analytics_endpoint(contrail_api_endpoint):
    """Return contrail analytics endpoint."""
    parse_result = parse.urlparse(contrail_api_endpoint)
    return parse_result._replace(netloc="{}:{}".format(
        parse_result.hostname, settings.CONTAIL_ANALYTICS_PORT)).geturl()


@pytest.fixture
def contrail_api_client(session, contrail_api_endpoint):
    """Return instance of contail client."""
    headers = {'Content-type': 'application/json; charset="UTF-8"'}
    headers.update(session.get_auth_headers())
    return client.Client(
        url=contrail_api_endpoint, headers=headers, blocking=False)
