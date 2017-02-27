# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from hamcrest import assert_that, has_entries, has_item
import pytest

from vapor.helpers import contrail_status
from vapor import settings

pytestmark = pytest.mark.requires('dpdk_enabled')


def test_contrail_vrouter_dpdk(os_faults_steps):
    """Validate existence and status for contrail-vrouter-dpdk service."""
    statuses = contrail_status.get_services_statuses(os_faults_steps)
    for fqdn in settings.CONTRAIL_ROLES_DISTRIBUTION[
            settings.ROLE_CONTRAIL_COMPUTE]:
        compute_services = statuses[fqdn]
        assert_that(
            compute_services,
            has_item(
                has_entries(name='contrail-vrouter-dpdk', status='active')))
