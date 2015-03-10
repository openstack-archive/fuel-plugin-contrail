# vim: tabstop=4 shiftwidth=4 softtabstop=4
#
# Copyright 2014 Juniper Networks.  All rights reserved.
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
#
# @author: Hampapur Ajay, Praneet Bachheti

import copy
import logging
from pprint import pformat
import sys

import cgitb

LOG = logging.getLogger(__name__)


class NeutronPluginContrailPolicy(object):
    def set_core(self, core_instance):
        self._core = core_instance

    def _make_policy_dict(self, entry, status_code=None, fields=None):
        return entry

    def create_policy(self, context, policy):
        """
        Creates a new Policy, and assigns it a symbolic name.
        """
        plugin_policy = copy.deepcopy(policy)

        policy_dicts = self._core._create_resource('policy', context,
                                                   plugin_policy)
        LOG.debug("create_policy(): " + pformat(policy_dicts) + "\n")

        return policy_dicts

    def get_policy(self, context, policy_id, fields=None):
        """
        Get the attributes of a policy.
        """
        policy_dicts = self._core._get_resource('policy', context, policy_id,
                                                fields)

        LOG.debug("get_policy(): " + pformat(policy_dicts))
        return policy_dicts

    def update_policy(self, context, policy_id, policy):
        """
        Updates the attributes of a particular policy.
        """
        plugin_policy = copy.deepcopy(policy)
        policy_dicts = self._core._update_resource('policy', context,
                                                   policy_id, plugin_policy)

        LOG.debug("update_policy(): " + pformat(policy_dicts))
        return policy_dicts

    def delete_policy(self, context, policy_id):
        """
        Deletes the Policy with the specified identifier
        """
        self._core._delete_resource('policy', context, policy_id)

        LOG.debug("delete_policy(): %s" % (policy_id))

    def get_policys(self, context, filters=None, fields=None):
        """
        Retrieves all policies identifiers.
        """
        policy_dicts = self._core._list_resource('policy', context, filters,
                                                 fields)

        LOG.debug(
            "get_policys(): filters: " + pformat(filters) + " data: "
            + pformat(policy_dicts))
        return policy_dicts

    def get_policy_count(self, context, filters=None):
        """
        Get the count of policies.
        """
        policies_count = self._core._count_resource('policy', context, filters)

        LOG.debug("get_policy_count(): filters: " + pformat(filters) +
                  " data: " + str(policies_count['count']))
        return policies_count['count']
