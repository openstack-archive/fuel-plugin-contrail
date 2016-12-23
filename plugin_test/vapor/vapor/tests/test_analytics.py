from hamcrest import assert_that, is_  # noqa H301


def test_contrail_alarms(client_contrail_analytics):
    alarms = client_contrail_analytics.get_alarms()
    assert_that(alarms, is_(dict))
