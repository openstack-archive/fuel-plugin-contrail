import xml.etree.ElementTree as ET

from hamcrest import is_not, empty
from stepler.third_party import waiter


def wait_db_purge_result(client, purge_id, timeout=0):
    def predicate():
        result = client.post_query(
            'StatTable.DatabasePurgeInfo.stats',
            start_time=0,
            end_time='now',
            select_fields=[
                'stats.purge_id', 'stats.purge_status',
                'stats.purge_status_details'
            ],
            where=[[{
                'name': 'stats.purge_id',
                'value': purge_id,
                'op': client.MatchOps.EQUAL
            }]],
            limit=1)
        waiter.expect_that(result['value'], is_not(empty()))
        return result['value'][0]
    return waiter.wait(predicate, timeout_seconds=timeout,
                       waiting_for='purge results to appear')


def get_collector_connectivity(session, ip, port):
    """Returns a dict with collector connection status."""
    response = session.get(
        'http://{ip}:{port}/Snh_CollectorInfoRequest?'.format(
            ip=ip, port=port))
    response.raise_for_status()
    tree = ET.fromstring(response.content)
    return {
        'ip': tree.find('ip').text,
        'port': tree.find('port').text,
        'status': tree.find('status').text,
    }


def get_vna_xmpp_connection_status(session, ip, port):
    """Returns a list with dicts."""
    response = session.get(
        'http://{ip}:{port}/Snh_AgentXmppConnectionStatusReq?'.format(
            ip=ip, port=port))
    response.raise_for_status()
    tree = ET.fromstring(response.content)
    agent_data_elements = tree.findall('.//list/AgentXmppData')

    result = []
    for agent_data_element in agent_data_elements:
        agent_dict = {}
        for tag in ('controller_ip', 'cfg_controller', 'state',):
            agent_dict[tag] = agent_data_element.find('./' + tag).text
        result.append(agent_dict)
    return result
