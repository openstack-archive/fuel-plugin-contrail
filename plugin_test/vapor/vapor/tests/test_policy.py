# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from hamcrest import assert_that, calling, raises
from pycontrail import exceptions
from pycontrail import types
from stepler import config as stepler_config

from vapor import settings
from vapor.helpers import connectivity


def test_delete_policy_associated_with_network(
        contrail_network, contrail_network_policy, set_network_policy,
        contrail_api_client):
    """Associate/Disassociate/Delete with reference policy using API.

    Steps:
        #. Create network
        #. Create policy
        #. Associate policy with network
        #. Check that deleting network with policy raises an Exception
    """
    set_network_policy(contrail_network, contrail_network_policy)
    assert_that(
        calling(contrail_api_client.network_policy_delete).with_args(
            id=contrail_network_policy.uuid),
        raises(exceptions.RefsExistError))
