"""Copyright 2015 Mirantis, Inc.

Licensed under the Apache License, Version 2.0 (the "License"); you may
not use this file except in compliance with the License. You may obtain
copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
License for the specific language governing permissions and limitations
under the License.
"""

import sys

import os
import re
from nose import plugins
from paramiko.transport import _join_lingering_threads


class CloseSSHConnectionsPlugin(plugins.Plugin):
    """Closes all paramiko's ssh connections after each test case.

    Plugin fixes proboscis disability to run cleanup of any kind.
    'afterTest' calls _join_lingering_threads function from paramiko,
    which stops all threads (set the state to inactive and joins for 10s)
    """

    name = 'closesshconnections'

    def options(self, parser, env=os.environ):
        """Options."""
        super(CloseSSHConnectionsPlugin, self).options(parser, env=env)

    def configure(self, options, conf):
        """Configure env."""
        super(CloseSSHConnectionsPlugin, self).configure(options, conf)
        self.enabled = True

    def afterTest(self, *args, **kwargs):
        """After_Test.

        After_Test calls _join_lingering_threads function from paramiko,
        which stops all threads (set the state to inactive and joins for 10s).
        """
        _join_lingering_threads()


def import_tests():
    """Import test suite of project."""
    from tests import test_smoke_bvt  # noqa
    from tests import test_integration  # noqa
    from tests import test_functional  # noqa
    from tests import test_failover  # noqa
    from tests import test_system  # noqa
    from tests import test_dpdk  # noqa
    from tests import test_sriov  # noqa
    from tests import test_dpdk_on_vf  # noqa
    from tests import test_contrail_multiple_networks  # noqa


def run_tests():
    """Run test cases."""
    from proboscis import TestProgram  # noqa
    import_tests()

    # Run Proboscis and exit.
    TestProgram(
        addplugins=[CloseSSHConnectionsPlugin()]
    ).run_and_exit()


if __name__ == '__main__':
    sys.path.append(sys.path[0] + "/fuel-qa")
    import_tests()
    from fuelweb_test.helpers.patching import map_test
    if any(re.search(r'--group=patching_master_tests', arg)
           for arg in sys.argv):
        map_test('master')
    elif any(re.search(r'--group=patching.*', arg) for arg in sys.argv):
        map_test('environment')
    run_tests()
