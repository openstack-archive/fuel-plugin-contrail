from hamcrest import assert_that, calling, raises  # noqa H301


def test_network_deleting_with_server(network, server, network_steps):
    # TODO(gdyuldin): Replace Exception with correct exception class
    assert_that(
        calling(network_steps.delete).with_args(network), raises(Exception))
