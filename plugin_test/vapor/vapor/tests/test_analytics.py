import dpath.util
import jmespath
from hamcrest import (assert_that, is_, empty, has_key, all_of,
                      equal_to)  # noqa H301
import pytest
from six.moves import filter

from vapor.helpers import analytic_steps
from vapor import settings


def test_contrail_alarms(client_contrail_analytics):
    alarms = client_contrail_analytics.get_alarms()
    assert_that(alarms, is_(dict))


def test_db_purge(client_contrail_analytics):
    purge_id = client_contrail_analytics.database_purge(
        purge_input=1)['purge_id']
    purge_results = analytic_steps.wait_db_purge_result(
        client_contrail_analytics, purge_id, timeout=settings.DB_PURGE_TIMEOUT)
    assert_that(purge_results['stats.purge_status'], is_('success'))


def test_collector_generator_connections_through_uves(
        session, client_contrail_analytics,
        contrail_services_http_introspect_ports):
    # Check collector-generator connections through uves
    for service, nodes in contrail_services_http_introspect_ports.items():
        port = nodes['port']
        for ip in nodes['ips']:
            status = analytic_steps.get_collector_connectivity(session, ip,
                                                               port)
            assert status['status'] == 'Established'

    for name in client_contrail_analytics.get_uves_generators():
        generator_data = client_contrail_analytics.get_uves_generator_data(
            name)
        client_info = dpath.util.get(generator_data, '/*/client_info')
        assert client_info['status'] == 'Established'


def test_vrouter_uve_xmpp_connections(session, client_contrail_analytics,
                                      contrail_services_http_introspect_ports,
                                      nodes_ips):

    contrail_controllers_fqdns = settings.CONTRAIL_ROLES_DISTRIBUTION[
        settings.ROLE_CONTRAIL_CONTROLLER]

    vrouter_generators = filter(
        lambda x: 'Compute:contrail-vrouter-agent' in x,
        client_contrail_analytics.get_uves_generators())
    for name in vrouter_generators:
        fqdn = name.split(':')[0]
        vrouter_ops = client_contrail_analytics.get_uves_vrouter_ops(fqdn)
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
                assert active_xmpp == vrouter_active_xmpp_peer
        # Verify vrouter uve for xmpp connections
        expected_connection_count = min(2, len(contrail_controllers_fqdns))
        actual_connections_count = 0
        peers = {peer['ip'] for peer in xmpp_peer_list}
        for fqdn in contrail_controllers_fqdns:
            if peers & set(nodes_ips[fqdn]):
                actual_connections_count += 1
        assert actual_connections_count == expected_connection_count


def test_peer_count_in_bgp_router_uve(client_contrail_analytics,
                                      contrail_services_http_introspect_ports,
                                      nodes_ips):
    # count of xmpp peer and bgp peer verification in bgp-router uve
    contrail_computes_fqdns = settings.CONTRAIL_ROLES_DISTRIBUTION[
        settings.ROLE_CONTRAIL_COMPUTE]
    contrail_controllers_fqdns = settings.CONTRAIL_ROLES_DISTRIBUTION[
        settings.ROLE_CONTRAIL_CONTROLLER]
    total_agent_connections = 0
    factor = min(2, len(contrail_controllers_fqdns))
    for name in client_contrail_analytics.get_uves_control_nodes():
        node_ops = client_contrail_analytics.get_uves_control_node_ops(name)
        agents_count = dpath.util.get(node_ops, '**/num_xmpp_peer')
        total_agent_connections += agents_count
        bgp_nodes_count = dpath.util.get(node_ops, '**/num_bgp_peer')
        # TODO: verify this check
        assert bgp_nodes_count == len(contrail_controllers_fqdns)

    assert total_agent_connections == len(contrail_computes_fqdns) * factor


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
    for node in client_contrail_analytics.get_uves_analytics_nodes():
        ops = client_contrail_analytics.get_uves_analytics_node_ops(node)
        bad_items = filter_(ops, module_id)
        assert_that(bad_items, is_(empty()), '{} has problems'.format(node))


@pytest.mark.parametrize(
    'filter_', [
        analytic_steps.get_processes_with_wrong_state,
        analytic_steps.get_process_with_wrong_connection_status,
    ],
    ids=['process_state', 'connection_status'])
def test_process_and_connection_infos_control_node(client_contrail_analytics,
                                                   filter_):
    for node in client_contrail_analytics.get_uves_control_nodes():
        ops = client_contrail_analytics.get_uves_control_node_ops(node)
        bad_items = filter_(ops, 'contrail-control')
        assert_that(bad_items, is_(empty()), '{} has problems'.format(node))


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
    for node in client_contrail_analytics.get_uves_config_nodes():
        ops = client_contrail_analytics.get_uves_config_node_ops(node)
        bad_items = filter_(ops, module_id)
        assert_that(bad_items, is_(empty()), '{} has problems'.format(node))


@pytest.mark.parametrize(
    'filter_', [
        analytic_steps.get_processes_with_wrong_state,
        analytic_steps.get_process_with_wrong_connection_status,
    ],
    ids=['process_state', 'connection_status'])
def test_process_and_connection_infos_compute_node(client_contrail_analytics,
                                                   filter_):
    for node in client_contrail_analytics.get_uves_vrouters():
        ops = client_contrail_analytics.get_uves_vrouter_ops(node)
        bad_items = filter_(ops, 'contrail-vrouter-agent')
        assert_that(bad_items, is_(empty()), '{} has problems'.format(node))


def test_verify_bgp_peer_uve(client_contrail_analytics):
    for peer_name in client_contrail_analytics.get_uves_bgp_peers():
        peer_info = client_contrail_analytics.get_uves_bgp_peer_info(peer_name)
        tx_proto_stats = jmespath.search(
            'BgpPeerInfoData.peer_stats_info.tx_proto_stats', peer_info)
        assert_that(tx_proto_stats,
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
                                               method_name):
    func = getattr(client_contrail_analytics, method_name)
    actual_hostnames = set(func())
    expected_hostnames = set(settings.CONTRAIL_ROLES_DISTRIBUTION[role])
    assert_that(actual_hostnames, equal_to(expected_hostnames))


@pytest.mark.parametrize(['role', 'method_name'], [
    (settings.ROLE_CONTRAIL_CONFIG, 'get_uves_config_node_ops'),
    (settings.ROLE_CONTRAIL_ANALYTICS, 'get_uves_analytics_node_ops'),
])
def test_uve_module_states(client_contrail_analytics, role, method_name):
    expected_process_list = settings.CONTRAIL_ANALYTIC_PROCESSES[role]
    func = getattr(client_contrail_analytics, method_name)
    for node in settings.CONTRAIL_ROLES_DISTRIBUTION[role]:
        data = func(node)
        process_list = jmespath.search(
            'NodeStatus.process_info[].process_name', data)
        process_list = map(lambda x: x.split(':')[0], process_list)
        absent_processes = set(expected_process_list) - set(process_list)
        assert_that(absent_processes, is_(empty()))
        wrong_processes = analytic_steps.get_process_info_with_wrong_state(
            data)
        assert_that(wrong_processes, is_(empty()))
