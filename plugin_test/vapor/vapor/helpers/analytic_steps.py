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
