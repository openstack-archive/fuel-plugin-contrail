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

LOG = logging.getLogger(__name__)


class NeutronPluginContrailVpc(object):
    def set_core(self, core_instance):
        self._core = core_instance

    # VPC route table handlers
    def _make_route_table_routes_dict(self, route_table_route, fields=None):
        res = {'prefix': route_table_route['prefix'],
               'next_hop': route_table_route['next_hop']}

        return self._core._fields(res, fields)

    def _make_route_table_dict(self, route_table, status_code=None,
                               fields=None):
        res = {'id': route_table['id'],
               'name': route_table['name'],
               'fq_name': route_table['fq_name'],
               'tenant_id': route_table['tenant_id']}
        if route_table['routes']:
            res['routes'] = [self._make_route_table_routes_dict(r)
                             for r in route_table['routes']['route']]
        else:
            res['routes'] = {}
        return self._core._fields(res, fields)

    def create_route_table(self, context, route_table):
        """
        Creates a Route Table.
        """
        plugin_rt = copy.deepcopy(route_table)

        rt_dicts = self._core._create_resource('route_table', context,
                                               plugin_rt)
        LOG.debug("create_route_table(): " + pformat(rt_dicts) + "\n")

        return rt_dicts

    def get_route_table(self, context, rt_id, fields=None):
        """
        Get the attributes of a route table.
        """
        rt_dicts = self._core._get_resource('route_table', context, rt_id,
                                            fields)

        LOG.debug("get_route_table(): " + pformat(rt_dicts))

        return rt_dicts

    def update_route_table(self, context, rt_id, route_table):
        """
        Updates the attributes of a particular route table.
        """
        plugin_rt = copy.deepcopy(route_table)
        rt_dicts = self._core._update_resource('route_table', context, rt_id,
                                               plugin_rt)

        LOG.debug("update_route_table(): " + pformat(rt_dicts))
        return rt_dicts

    def delete_route_table(self, context, rt_id):
        """
        Deletes a route table
        """
        self._core._delete_resource('route_table', context,
                                                    rt_id)

        LOG.debug("delete_security_group(): %s" % (rt_id))

    def get_route_tables(self, context, filters=None, fields=None,
                         sorts=None, limit=None, marker=None,
                         page_reverse=False):
        """
        Retrieves all route tables
        """
        rt_dicts = self._core._list_resource('route_table', context, filters,
                                             fields)

        LOG.debug(
            "get_route_tables(): filters: " + pformat(filters) + " data: "
            + pformat(rt_dicts))
        return rt_dicts

    # VPC route table nat instance handlers
    def _make_nat_instance_dict(self, nat_instance, status_code=None,
                                fields=None):
        res = {'id': nat_instance['id'],
               'name': nat_instance['name'],
               'tenant_id': nat_instance['tenant_id']}
        if nat_instance['internal_net']:
            res['internal_net'] = nat_instance['internal_net']
        if nat_instance['external_net']:
            res['external_net'] = nat_instance['external_net']
        return self._core._fields(res, fields)

    def create_nat_instance(self, context, nat_instance):
        """
        Creates a new nat instance
        """
        plugin_nat = copy.deepcopy(nat_instance)

        nat_dicts = self._core._create_resource('nat_instance', context,
                                                plugin_nat)

        LOG.debug("create_nat_instance(): " + pformat(nat_dicts) + "\n")
        return nat_dicts

    def get_nat_instance(self, context, nat_id, fields=None):
        """
        Get the attributes of a particular nat instance
        """
        nat_dicts = self._core._get_resource('nat_instance', context, nat_id,
                                             fields)

        LOG.debug("get_nat_instance(): " + pformat(nat_dicts))
        return self._core._fields(nat_dicts, fields)

    def delete_nat_instance(self, context, nat_id):
        """
        Deletes the nat instance
        """
        self._core._delete_resource('nat_instance', context, nat_id)

        LOG.debug("delete_nat_instance(): %s" % (nat_id))

    def get_nat_instances(self, context, filters=None, fields=None,
                          sorts=None, limit=None, marker=None,
                          page_reverse=False):
        """
        Get the list of nat instances.
        """
        nat_dicts = self._core._list_resource('nat_instance', context,
                                              filters, fields)

        LOG.debug(
            "get_nat_instances(): filters: " + pformat(filters) + " data: "
            + pformat(nat_dicts))
        return nat_dicts
