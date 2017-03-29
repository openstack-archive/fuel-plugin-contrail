import os
import six
import uuid
import pytest
import logbook

import pycontrail.client as client
from six.moves import configparser


from vapor import settings
from vapor.helpers import clients

LOGGER = logbook.Logger(__name__)


@pytest.fixture
def client_contrail(session):
    with clients.ContrailClient(session,
                                settings.CONTRAIL_API_URL) as contrail:
        yield contrail


@pytest.fixture
def client_contrail_analytics(session):
    return clients.ContrailAnalyticsClient(session,
                                           settings.CONTRAIL_ANALYTICS_URL)


@pytest.fixture
def client_contrail_vrouter_agent(contrail_vrouter_agent_endpoint):
    LOGGER.debug('VRouter endpoint: {0}'.format(
        contrail_vrouter_agent_endpoint))
    return clients.ContrailVRouterAgentClient(
        agent_ip=contrail_vrouter_agent_endpoint['ip'],
        agent_port=contrail_vrouter_agent_endpoint['port'])


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
            fqdns=settings.CONTRAIL_ROLES_DISTRIBUTION[role])

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
def contrail_vrouter_agent_endpoint(contrail_services_http_introspect_ports):
    """Return contrail agent endpoint."""
    service_name = 'contrail-vrouter-agent'
    ip = contrail_services_http_introspect_ports[service_name]['nodes'][0][
        'ip']
    port = contrail_services_http_introspect_ports[service_name]['port']
    return {'ip': ip, 'port': port}


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
                results[service_name]['nodes'].append({
                    'ip': node_ip,
                    'fqdn': node.get_fqdns()[0]
                })
                continue
            if service_name not in default_ports:
                continue
            port = default_ports[service_name]
            temp_file = os_faults_steps.download_file(node, path)
            parser = configparser.SafeConfigParser()
            # Strip leading spaces in .conf file
            buf = six.BytesIO()
            with open(temp_file) as f:
                for line in f:
                    buf.write(line.strip())
            os.unlink(temp_file)
            parser.readfp(buf)
            try:
                service_config = dict(parser.items('DEFAULT'))
                port = service_config.get('http_server_port', port)
            except configparser.NoSectionError:
                pass
            if port:
                results[service_name] = {
                    'port': port,
                    'nodes': [{
                        'ip': node_ip,
                        'fqdn': node.get_fqdns()[0]
                    }],
                }
    return results


@pytest.fixture
def contrail_api_client(session):
    """Return instance of contail client."""
    headers = {'Content-type': 'application/json; charset="UTF-8"'}
    headers.update(session.get_auth_headers())
    return client.Client(
        url=settings.CONTRAIL_API_URL, headers=headers, blocking=False)


@pytest.fixture
def default_project(contrail_api_client):
    proj_id = contrail_api_client.project_get_default_id()
    return contrail_api_client.project_read(id=proj_id)


@pytest.fixture
def default_domain(contrail_api_client):
    domain_id = contrail_api_client.domain_get_default_id()
    return contrail_api_client.domain_read(id=domain_id)


@pytest.fixture
def contrail_current_project(contrail_api_client, current_project):
    project_id = str(uuid.UUID(current_project.id))
    return contrail_api_client.project_read(id=project_id)


@pytest.fixture
def iface_route_table_create(contrail_api_client):
    """Callable fixture to create interface router table during test.

    All created tables will be deleted after test.
    """
    tables = []

    def _iface_route_table_create(iface_route_table):
        tables.append(iface_route_table)
        contrail_api_client.interface_route_table_create(iface_route_table)

    yield _iface_route_table_create

    for table in reversed(tables):
        contrail_api_client.interface_route_table_delete(id=table.uuid)
