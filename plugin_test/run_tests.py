#    Copyright 2015 Mirantis, Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import sys
import functools
import logging
import os
import re
from nose.plugins import Plugin
from paramiko.transport import _join_lingering_threads


class CloseSSHConnectionsPlugin(Plugin):
    """Closes all paramiko's ssh connections after each test case

    Plugin fixes proboscis disability to run cleanup of any kind.
    'afterTest' calls _join_lingering_threads function from paramiko,
    which stops all threads (set the state to inactive and joins for 10s)
    """
    name = 'closesshconnections'

    def options(self, parser, env=os.environ):
        super(CloseSSHConnectionsPlugin, self).options(parser, env=env)

    def configure(self, options, conf):
        super(CloseSSHConnectionsPlugin, self).configure(options, conf)
        self.enabled = True

    def afterTest(self, *args, **kwargs):
        _join_lingering_threads()


def import_tests():
    from tests import test_fuel_plugin_contrail


def run_tests():
    from proboscis import TestProgram  # noqa
    import_tests()

    # Run Proboscis and exit.
    TestProgram(
        addplugins=[CloseSSHConnectionsPlugin()]
    ).run_and_exit()


if __name__ == '__main__':
    sys.path.append(sys.path[0]+"/fuel-qa")


    from fuelweb_test.settings import LOGS_DIR
    if not os.path.exists(LOGS_DIR):
            os.makedirs(LOGS_DIR)
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s - %(levelname)s %(filename)s:'
                        '%(lineno)d -- %(message)s',
                        filename=os.path.join(LOGS_DIR, 'sys_test.log'),
                        filemode='w')
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s %(filename)s:'
                                  '%(lineno)d -- %(message)s')
    console.setFormatter(formatter)
    logger = logging.getLogger(__name__)
    logger.addHandler(console)
    class NoDebugMessageFilter(logging.Filter):
        def filter(self, record):
            return not record.levelno <= logging.DEBUG
    
    logging.getLogger('paramiko.transport').addFilter(NoDebugMessageFilter())
    logging.getLogger('paramiko.hostkeys').addFilter(NoDebugMessageFilter())
    logging.getLogger('iso8601.iso8601').addFilter(NoDebugMessageFilter())

    def debug(logger):
        def wrapper(func):
            @functools.wraps(func)
            def wrapped(*args, **kwargs):
                logger.debug(
                    "Calling: {} with args: {} {}".format(
                         func.__name__, args, kwargs
                    )
                )
                result = func(*args, **kwargs)
                logger.debug(
                    "Done: {} with result: {}".format(func.__name__, result))
                return result
            return wrapped
        return wrapper
    logwrap = debug(logger)
    class quiet_logger(object):
         """Reduce logging level while context is executed."""

         def __enter__(self):
             console.setLevel(logging.ERROR)

         def __exit__(self, exp_type, exp_value, traceback):
             console.setLevel(logging.INFO)




    import_tests()
    from fuelweb_test.helpers.patching import map_test
    if any(re.search(r'--group=patching_master_tests', arg)
           for arg in sys.argv):
        map_test('master')
    elif any(re.search(r'--group=patching.*', arg) for arg in sys.argv):
        map_test('environment')
    run_tests()
