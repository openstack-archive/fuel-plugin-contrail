"""Copyright 2016 Mirantis, Inc.

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
from fuelweb_test import logwrap
from fuelweb_test import logger
from fuelweb_test.helpers.decorators import json_parse
from fuelweb_test.helpers.http import HTTPClient
from fuelweb_test.settings import KEYSTONE_CREDS


class ContrailClient(object):
    """Contrail utilite wrapper."""

    def __init__(self, controller_node_ip, **kwargs):
        """Create ContrailClient object."""
        url = "http://{0}:8082".format(controller_node_ip)
        logger.info('Initiate Nailgun client with url %s', url)
        self.keystone_url = "http://{0}:5000/v2.0".format(controller_node_ip)
        self._client = HTTPClient(url=url, keystone_url=self.keystone_url,
                                  credentials=KEYSTONE_CREDS,
                                  **kwargs)
        super(ContrailClient, self).__init__()

    @property
    def client(self):
        """Client property."""
        return self._client

    @logwrap
    @json_parse
    def create_network(self, net_name, net_attr):
        """Create virtual-network.

        :param project_name: type list, tenant(project), network name
        :param net_attr: type dictionary, network attributes
        """
        data = {
            "virtual-network": {
                "parent_type": "project",
                "fq_name": net_name,
                "network_ipam_refs": net_attr}}
        return self.client.post(
            '/virtual-networks', data=data)['virtual-network']

    def add_router_interface(self, network, route_table, attr=None):
        """Add router interface to network.

        :param network: type dictionary, network
        :param route_table: type dictionary, router
        :param attr: type dictionary, parameters of router interface(optianal)
        """
        data = {"virtual-network": {'fq_name': network['fq_name'],
                'route_table_refs': [{
                    'to': route_table['fq_name'], "attr":attr}]}}
        return self.client.put(
            '/virtual-network/{0}'.format(network['uuid']), data=data)

    def get_route_tables(self):
        """Get router."""
        return self.client.get('/route-tables')

    def get_router_by_name(self, name):
        """Get router by name.

        :param name: type string, name of router.
        :return dictionary
        """
        route_tables = self.get_route_tables()['route-tables']
        route_table = [
            route for route in route_tables
            if name in route['fq_name']]
        return route_table

    def get_projects(self):
        """Get router."""
        return self.client.get('/projects')

    def get_project_by_name(self, name):
        """Get project by name.

        :param name: type string, name of project.
        :return dictionary
        """
        projects = self.get_projects()
        project = [p for p in projects if name in p['fq_name']]
        return project

    def get_instance_by_id(self, instance_id):
        """Get instance by id.

        :param instance_id: type string, instance id.
        :return dictionary
        """
        return self.client.get(
            '/virtual-machine/{0}'.format(instance_id))['virtual-machine']

    def get_net_by_id(self, net_id):
        """Get network by id.

        :param net_id: type string, instance id.
        :return dictionary
        """
        return self.client.get(
            '/virtual-network/{0}'.format(net_id))['virtual-network']
