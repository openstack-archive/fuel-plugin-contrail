# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import pytest
import six
from stepler.fixtures import skip

from vapor import settings


class Predicates(skip.Predicates):

    _store_call = six.get_unbound_function(skip.Predicates._store_call)

    @property
    @_store_call
    def vrouter_headless_mode(self):
        """Define whether vrouter headless mode enabled."""
        os_faults_steps = self._get_fixture('os_faults_steps')
        fqdns = settings.CONRTAIL_ROLES_DISTRIBUTION[settings.
                                                     ROLE_CONTRAIL_COMPUTE]
        actual_nodes = os_faults_steps.get_nodes_by_cmd(
            settings.VROUTER_HEADLESS_MODE_CMD)
        return set(actual_nodes.get_fqdns()) == set(fqdns)


@pytest.fixture
def predicates(request):
    return Predicates(request)
