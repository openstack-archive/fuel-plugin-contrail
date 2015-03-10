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


class NeutronPluginContrailIpam(object):
    def set_core(self, core_instance):
        self._core = core_instance

    def _make_ipam_dict(self, entry, status_code=None, fields=None):
        return entry

    def create_ipam(self, context, ipam):
        """
        Creates a new ipam, and assigns it a symbolic name.
        """
        plugin_ipam = copy.deepcopy(ipam)

        ipam_dicts = self._core._create_resource('ipam', context, plugin_ipam)
        LOG.debug("create_ipam(): " + pformat(ipam_dicts) + "\n")

        return ipam_dicts

    def get_ipam(self, context, ipam_id, fields=None):
        """
        Get the attributes of a ipam.
        """
        ipam_dicts = self._core._get_resource('ipam', context, ipam_id, fields)

        LOG.debug("get_ipam(): " + pformat(ipam_dicts))
        return ipam_dicts

    def update_ipam(self, context, ipam_id, ipam):
        """
        Updates the attributes of a particular ipam.
        """
        plugin_ipam = copy.deepcopy(ipam)
        ipam_dicts = self._core._update_resource('ipam', context, ipam_id,
                                           plugin_ipam)

        LOG.debug("update_ipam(): " + pformat(ipam_dicts))
        return ipam_dicts

    def delete_ipam(self, context, ipam_id):
        """
        Deletes the ipam with the specified identifier.
        """
        self._core._delete_resource('ipam', context, ipam_id)

        LOG.debug("delete_ipam(): %s" % (ipam_id))

    def get_ipams(self, context, filters=None, fields=None):
        """
        Retrieves all ipams identifiers.
        """
        ipam_dicts = self._core._list_resource('ipam', context, filters,
                                               fields)

        LOG.debug(
            "get_ipams(): filters: " + pformat(filters) + " data: "
            + pformat(ipam_dicts))
        return ipam_dicts

    def get_ipams_count(self, context, filters=None):
        """
        Get the count of ipams.
        """
        ipams_count = self._core._count_resource('ipam', context, filters)

        LOG.debug("get_ipams_count(): filters: " + pformat(filters) +
                  " data: " + str(ipams_count['count']))
        return ipams_count['count']
