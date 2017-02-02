"""
Pytest plugin to mark tests with xfail from config yaml file.

Note:

    Xfail file should be valid yaml file with format:

    .. code:: yaml

       test_name: reason
       vapor/tests/common/test_sg_policy.py::another_test_name: // WO reason
       yet_more_test_name: reason2
"""

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import pytest
import yaml


def pytest_addoption(parser):
    """Add ``--xfail-file`` option to pytest."""
    parser.addoption("--xfail-file", action="store", default='xfail.yaml',
                     help="Path to yaml file with xfail marks for tests.")


@pytest.hookimpl(trylast=True)
def pytest_collection_modifyitems(config, items):
    """Hook to skip tests with opened bugs."""
    if not config.option.xfail_file:
        return

    with open(config.option.xfail_file) as f:
        xfails = yaml.safe_load(f)

    for item in items:
        for key, message in xfails.items():
            if key == item.name or key == item.nodeid:
                item.add_marker(pytest.mark.xfail(reason=message))
