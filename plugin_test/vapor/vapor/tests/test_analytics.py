from hamcrest import assert_that, is_  # noqa H301

from vapor.helpers import contrail_status


def test_contrail_database_status(os_faults_steps, contrail_db_nodes):
    contrail_status.check_services(os_faults_steps, contrail_db_nodes)


def test_contrail_analytics_status(os_faults_steps, contrail_analytics_nodes):
    contrail_status.check_services(os_faults_steps, contrail_analytics_nodes)


def test_contrail_alarms(client_contrail_analytics):
    alarms = client_contrail_analytics.get_alarms()
    assert_that(alarms, is_(dict))
