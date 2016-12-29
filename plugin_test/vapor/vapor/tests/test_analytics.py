from hamcrest import assert_that, is_  # noqa H301

from vapor.helpers import analytic_steps
from vapor import settings


def test_contrail_alarms(client_contrail_analytics):
    alarms = client_contrail_analytics.get_alarms()
    assert_that(alarms, is_(dict))


def test_db_purge(client_contrail_analytics):
    purge_id = client_contrail_analytics.database_purge(
        purge_input=20)['purge_id']
    purge_results = analytic_steps.wait_db_purge_result(
        client_contrail_analytics, purge_id, timeout=settings.DB_PURGE_TIMEOUT)
    assert_that(purge_results['stats.purge_status'], is_('success'))
