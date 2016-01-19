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

import re

from fuelweb_test import logger


def node_rename(fuel_web, node_name_regexp, new_name, update_all=False):
    """Update nodes with new name
    """
    re_obj = re.compile(node_name_regexp)
    configured_nodes = fuel_web.client.list_nodes()

    nodes4update = []
    for node in configured_nodes:
        node_data = {
            'cluster_id': node['cluster'],
            'id': node['id'],
            'pending_addition': node['pending_addition'],
            'pending_deletion': node['pending_deletion'],
            'pending_roles': node['pending_roles'],
        }
        if re_obj.match(node['name']):
            logger.info("RENAME NODE  '%s' to '%s'" % (node['name'], new_name))
            node_data['name'] = new_name
            nodes4update.append(node_data)
        else:
            if update_all:
                node_data['name'] = node['name']
                nodes4update.append(node_data)

    return fuel_web.client.update_nodes(nodes4update)
