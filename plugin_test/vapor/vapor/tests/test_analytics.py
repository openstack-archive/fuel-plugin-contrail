import dpath.util
import jmespath
from hamcrest import (assert_that, is_, empty, has_key, all_of, has_length,
                      equal_to)  # noqa H301
import pytest
from six.moves import filter

from vapor.helpers import analytic_steps
from vapor.helpers import asserts
from vapor.helpers.asserts import superset_of
from vapor import settings


def test_contrail_alarms(client_contrail_analytics):
    """Check that contrail alarms endpoint returns a dict."""
    alarms = client_contrail_analytics.get_alarms()
    assert_that(alarms, is_(dict))


def test_db_purge(client_contrail_analytics):
    """Verify db purge result in database."""
    purge_id = client_contrail_analytics.database_purge(
        purge_input=1)['purge_id']
    purge_results = analytic_steps.wait_db_purge_result(
        client_contrail_analytics, purge_id, timeout=settings.DB_PURGE_TIMEOUT)
    assert_that(purge_results['stats.purge_status'], is_('success'))


def test_collector_generator_connections_through_uves(
        session, client_contrail_analytics,
        contrail_services_http_introspect_ports):
    """Check collector generator connections through UVES."""
    with asserts.AssertsCollector() as collector:
        for _, nodes in contrail_services_http_introspect_ports.items():
            port = nodes['port']
            for ip in nodes['ips']:
                status = analytic_steps.get_collector_connectivity(session, ip,
                                                                   port)
                collector.check(status['status'], is_('Established'))

        for name in client_contrail_analytics.get_uves_generators():
            generator_data = client_contrail_analytics.get_uves_generator_data(
                name)
            client_info = dpath.util.get(generator_data, '/*/client_info')
            collector.check(client_info['status'], is_('Established'))


def test_vrouter_uve_xmpp_connections(session, client_contrail_analytics,
                                      contrail_services_http_introspect_ports,
                                      nodes_ips, os_faults_steps):
    """Check vrouter UVE XMPP connections."""
    contrail_controllers_fqdns = settings.CONTRAIL_ROLES_DISTRIBUTION[
        settings.ROLE_CONTRAIL_CONTROLLER]

    vrouter_generators = filter(
        lambda x: 'Compute:contrail-vrouter-agent' in x,
        client_contrail_analytics.get_uves_generators())
    with asserts.AssertsCollector() as collector:
        for name in vrouter_generators:
            host = name.split(':')[0]
            fqdn = os_faults_steps.get_fqdn_by_host_name(host)
            vrouter_ops = client_contrail_analytics.get_uves_vrouter_ops(host)
            xmpp_peer_list = dpath.util.get(vrouter_ops, '**/xmpp_peer_list')
            vrouter_active_xmpp_peer = next(
                filter(lambda x: x['primary'], xmpp_peer_list))['ip']
            ip = nodes_ips[fqdn][0]
            port = contrail_services_http_introspect_ports[
                'contrail-vrouter-agent']['port']
            xmpp_conn_status = analytic_steps.get_vna_xmpp_connection_status(
                session, ip, port)
            # Verify vrouter uve active xmpp connections
            for elem in xmpp_conn_status:
                if elem['cfg_controller'] == 'Yes':
                    active_xmpp = elem['controller_ip']
                    collector.check(active_xmpp,
                                    equal_to(vrouter_active_xmpp_peer))
            # Verify vrouter uve for xmpp connections
            expected_connection_count = min(2, len(contrail_controllers_fqdns))
            actual_connections_count = 0
            peers = {peer['ip'] for peer in xmpp_peer_list}
            for fqdn in contrail_controllers_fqdns:
                if peers & set(nodes_ips[fqdn]):
                    actual_connections_count += 1
            collector.check(actual_connections_count,
                            equal_to(expected_connection_count))


def test_peer_count_in_bgp_router_uve(client_contrail_analytics):
    """Check count of XMPP peer and BGP peer verification in bgp-router UVE."""
    contrail_computes_fqdns = settings.CONTRAIL_ROLES_DISTRIBUTION[
        settings.ROLE_CONTRAIL_COMPUTE]
    contrail_controllers_fqdns = settings.CONTRAIL_ROLES_DISTRIBUTION[
        settings.ROLE_CONTRAIL_CONTROLLER]
    total_agent_connections = 0
    factor = min(2, len(contrail_controllers_fqdns))

    with asserts.AssertsCollector() as collector:
        for name in client_contrail_analytics.get_uves_control_nodes():
            node_ops = client_contrail_analytics.get_uves_control_node_ops(
                name)
            agents_count = dpath.util.get(node_ops, '**/num_xmpp_peer')
            total_agent_connections += agents_count
            bgp_nodes_count = dpath.util.get(node_ops, '**/num_bgp_peer')
            # TODO: verify this check
            collector.check(contrail_controllers_fqdns,
                            has_length(bgp_nodes_count))

        collector.check(contrail_computes_fqdns,
                        has_length(total_agent_connections / factor))


@pytest.mark.parametrize(
    'module_id',
    settings.CONTRAIL_CONNECTIONS[settings.ROLE_CONTRAIL_ANALYTICS])
@pytest.mark.parametrize(
    'filter_', [
        analytic_steps.get_processes_with_wrong_state,
        analytic_steps.get_process_with_wrong_connection_status,
    ],
    ids=['process_state', 'connection_status'])
def test_process_connection_infos_analytics_node(client_contrail_analytics,
                                                 module_id, filter_):
    """Check process connection infos for analytics node."""
    with asserts.AssertsCollector() as collector:
        for node in client_contrail_analytics.get_uves_analytics_nodes():
            ops = client_contrail_analytics.get_uves_analytics_node_ops(node)
            bad_items = filter_(ops, module_id)
            collector.check(bad_items,
                            is_(empty()), '{} has problems'.format(node))


@pytest.mark.parametrize(
    'filter_', [
        analytic_steps.get_processes_with_wrong_state,
        analytic_steps.get_process_with_wrong_connection_status,
    ],
    ids=['process_state', 'connection_status'])
def test_process_and_connection_infos_control_node(client_contrail_analytics,
                                                   filter_):
    """Check process and connection infos for control node."""
    with asserts.AssertsCollector() as collector:
        for node in client_contrail_analytics.get_uves_control_nodes():
            ops = client_contrail_analytics.get_uves_control_node_ops(node)
            bad_items = filter_(ops, 'contrail-control')
            collector.check(bad_items,
                            is_(empty()), '{} has problems'.format(node))


@pytest.mark.parametrize(
    'module_id', settings.CONTRAIL_CONNECTIONS[settings.ROLE_CONTRAIL_CONFIG])
@pytest.mark.parametrize(
    'filter_', [
        analytic_steps.get_processes_with_wrong_state,
        analytic_steps.get_process_with_wrong_connection_status,
    ],
    ids=['process_state', 'connection_status'])
def test_process_and_connection_infos_config_node(client_contrail_analytics,
                                                  module_id, filter_):
    """Check process and connection infos for config node."""
    with asserts.AssertsCollector() as collector:
        for node in client_contrail_analytics.get_uves_config_nodes():
            ops = client_contrail_analytics.get_uves_config_node_ops(node)
            bad_items = filter_(ops, module_id)
            collector.check(bad_items,
                            is_(empty()), '{} has problems'.format(node))


@pytest.mark.parametrize(
    'filter_', [
        analytic_steps.get_processes_with_wrong_state,
        analytic_steps.get_process_with_wrong_connection_status,
    ],
    ids=['process_state', 'connection_status'])
def test_process_and_connection_infos_compute_node(client_contrail_analytics,
                                                   filter_):
    """Check process and connection infos for compute node."""
    with asserts.AssertsCollector() as collector:
        for node in client_contrail_analytics.get_uves_vrouters():
            ops = client_contrail_analytics.get_uves_vrouter_ops(node)
            bad_items = filter_(ops, 'contrail-vrouter-agent')
            collector.check(bad_items,
                            is_(empty()), '{} has problems'.format(node))


def test_verify_bgp_peer_uve(client_contrail_analytics):
    """Verify BGP peer UVE."""
    with asserts.AssertsCollector() as collector:
        for peer_name in client_contrail_analytics.get_uves_bgp_peers():
            peer_info = client_contrail_analytics.get_uves_bgp_peer_info(
                peer_name)
            tx_proto_stats = jmespath.search(
                'BgpPeerInfoData.peer_stats_info.tx_proto_stats', peer_info)
            collector.check(tx_proto_stats,
                            all_of(
                                has_key('close'),
                                has_key('open'),
                                has_key('total'), ))


@pytest.mark.parametrize(['role', 'method_name'], [
    (settings.ROLE_CONTRAIL_CONTROLLER, 'get_uves_control_nodes'),
    (settings.ROLE_CONTRAIL_COMPUTE, 'get_uves_vrouters'),
    (settings.ROLE_CONTRAIL_ANALYTICS, 'get_uves_analytics_nodes'),
    (settings.ROLE_CONTRAIL_CONFIG, 'get_uves_config_nodes'),
])
def test_hrefs_to_all_uves_of_a_given_uve_type(client_contrail_analytics, role,
                                               method_name, os_faults_steps):
    """Verify hrefs to all UVEs of a given UVE type."""
    func = getattr(client_contrail_analytics, method_name)
    actual_hostnames = {
        os_faults_steps.get_fqdn_by_host_name(x)
        for x in func()
    }
    expected_hostnames = set(settings.CONTRAIL_ROLES_DISTRIBUTION[role])
    assert_that(actual_hostnames, equal_to(expected_hostnames))


@pytest.mark.parametrize(
    ['role', 'get_nodes_method_name', 'get_ops_method_name'], [
        (settings.ROLE_CONTRAIL_CONFIG, 'get_uves_config_nodes',
         'get_uves_config_node_ops'),
        (settings.ROLE_CONTRAIL_ANALYTICS, 'get_uves_analytics_nodes',
         'get_uves_analytics_node_ops'),
    ],
    ids=['config', 'analytics'])
def test_uve_module_states(client_contrail_analytics, os_faults_steps, role,
                           get_nodes_method_name, get_ops_method_name):
    """Verify UVE module states."""
    expected_process_list = settings.CONTRAIL_ANALYTIC_PROCESSES[role]
    get_nodes = getattr(client_contrail_analytics, get_nodes_method_name)
    get_ops = getattr(client_contrail_analytics, get_ops_method_name)
    # Map nodes to fqdns
    nodes = []
    fqdns = settings.CONTRAIL_ROLES_DISTRIBUTION[role]
    for node in get_nodes():
        if os_faults_steps.get_fqdn_by_host_name(node) in fqdns:
            nodes.append(node)
    with asserts.AssertsCollector() as collector:
        for node in nodes:
            data = get_ops(node)
            process_list = jmespath.search(
                'NodeStatus.process_info[].process_name', data)
            process_list = [x.split(':')[0] for x in process_list]
            collector.check(process_list,
                            superset_of(expected_process_list),
                            'Processes are absent on {}'.format(node))
            wrong_processes = analytic_steps.get_process_info_with_wrong_state(
                data)
            collector.check(wrong_processes,
                            is_(empty()),
                            'Processes has wrong status on {}'.format(node))
