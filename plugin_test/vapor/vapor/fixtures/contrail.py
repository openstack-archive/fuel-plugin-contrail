import os

import pycontrail.client as client
import pytest
from six.moves import configparser
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


def get_nodes_fixture(cmd, scope='function'):
    """Fixtures to gen nodes by cmd factory."""

    @pytest.fixture(scope=scope)
    def nodes_fixture(os_faults_steps):
        return os_faults_steps.get_nodes_by_cmd(cmd)

    return nodes_fixture


contrail_nodes = get_nodes_fixture('contrail-status | grep .', scope='module')


def get_contrail_nodes_fixture(role):
    """Fixtures to get contrail nodes by role."""

    @pytest.fixture(scope='module')
    def nodes_fixture(os_faults_steps):
        return os_faults_steps.get_nodes(
            fqdns=settings.CONRTAIL_ROLES_DISTRIBUTION[role])

    return nodes_fixture


contrail_controllers = get_contrail_nodes_fixture(
    settings.ROLE_CONTRAIL_CONTROLLER)

contrail_db_nodes = get_contrail_nodes_fixture(settings.ROLE_CONTRAIL_DB)

contrail_analytics_nodes = get_contrail_nodes_fixture(
    settings.ROLE_CONTRAIL_ANALYTICS)


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


@pytest.fixture(scope='module')
def contrail_services_http_introspect_ports(os_faults_steps, contrail_nodes):
    """Return contrail services ips and ports."""

    default_ports = {
        'contrail-config-nodemgr': 8100,
        'contrail-control-nodemgr': 8101,
        'contrail-vrouter-nodemgr': 8102,
        'contrail-database-nodemgr': 8103,
        'contrail-analytics-nodemgr': 8104,
        'contrail-storage-statsmgr': 8105,
        'contrail-control': 8083,
        'contrail-api-server': 8084,
        'contrail-vrouter-agent': 8085,
        'contrail-schema-transformer': 8087,
        'contrail-svc-monitor': 8088,
        'contrail-collector': 8089,
        'contrail-opserver': 8090,
        'contrail-query-engine': 8091,
        'contrail-dns': 8092
    }

    results = {}
    for node in contrail_nodes:
        node_ip = node.ip
        node = os_faults_steps.get_node(fqdns=[node.fqdn])
        result = os_faults_steps.execute_cmd(
            node, 'find {} -name contrail-*.conf -maxdepth 1'.format(
                settings.CONTRAIL_CONFIG_PATH))
        paths = result[0].payload['stdout_lines']
        for path in paths:
            filename = os.path.basename(path)
            service_name = os.path.splitext(filename)[0]
            if service_name in results:
                results[service_name]['ips'].append(node_ip)
                continue
            if service_name not in default_ports:
                continue
            port = default_ports[service_name]
            temp_file = os_faults_steps.download_file(node, path)
            parser = configparser.SafeConfigParser()
            with open(temp_file) as f:
                parser.readfp(f)
            os.unlink(temp_file)
            try:
                service_config = dict(parser.items('DEFAULT'))
                port = service_config.get('http_server_port', port)
            except configparser.NoSectionError:
                pass
            if port:
                results[service_name] = {'port': port, 'ips': [node_ip]}
    return results


@pytest.fixture
def contrail_api_client(session, contrail_api_endpoint):
    """Return instance of contail client."""
    headers = {'Content-type': 'application/json; charset="UTF-8"'}
    headers.update(session.get_auth_headers())
    return client.Client(
        url=contrail_api_endpoint, headers=headers, blocking=False)


@pytest.fixture
def nodes_ips(os_faults_steps):
    """Return dict node_fqdn -> node_ips."""
    nodes = os_faults_steps.get_nodes()
    ip_fqdn = {node.ip: node.fqdn for node in nodes}
    cmd = """ip -o a | awk '/scope global/{split($4,ip,"/"); print ip[1]}'"""
    results = os_faults_steps.execute_cmd(nodes, cmd)
    node_ips_ = {}
    for node_result in results:
        fqdn = ip_fqdn[node_result.host]
        node_ips_[fqdn] = node_result.payload['stdout_lines']

    return node_ips_


@pytest.fixture
def default_project(contrail_api_client):
    proj_id = contrail_api_client.project_get_default_id()
    return contrail_api_client.project_read(id=proj_id)
