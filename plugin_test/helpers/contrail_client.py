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
from fuelweb_test.settings import KEYSTONE_CREDS
from fuelweb_test.settings import PATH_TO_CERT
from fuelweb_test.settings import VERIFY_SSL
from fuelweb_test.settings import DISABLE_SSL


class ContrailClient(object):
    """Contrail utilite wrapper."""

    def __init__(self, controller_node_ip, contrail_port=8082,
                 credentials=KEYSTONE_CREDS, **kwargs):
        """Create ContrailClient object."""
        if DISABLE_SSL:
            url = "http://{0}:{1}".format(controller_node_ip, contrail_port)
            self.keystone_url = "http://{0}:5000/v2.0".format(
                controller_node_ip)
        else:
            url = "https://{0}:{1}".format(controller_node_ip, contrail_port)
            self.keystone_url = 'https://{0}:5000/v2.0/'.format(
                controller_node_ip)
            insecure = not VERIFY_SSL
            credentials.update({'ca_cert': PATH_TO_CERT, 'insecure': insecure})
        logger.info('Initiate Contrail client with url %s', url)
        #TODO add auth
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
            '/virtual-networks', data=data)

    @json_parse
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

    @json_parse
    def get_route_tables(self):
        """Get router."""
        return self.client.get('/route-tables')

    @json_parse
    def get_networks(self):
        """Get networks."""
        return self.client.get('/virtual-networks')

    def get_router_by_name(self, name):
        """Get router by name.

        :param name: type string, name of router.
        :return dictionary
        """
        route_tables = self.get_route_tables()['route-tables']
        route_table = [
            route for route in route_tables
            if name in route['fq_name']]
        return route_table.pop()

    @json_parse
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
        return project.pop()

    @json_parse
    def get_instance_by_id(self, instance_id):
        """Get instance by id.

        :param instance_id: type string, instance id.
        :return dictionary
        """
        return self.client.get(
            '/virtual-machine/{0}'.format(instance_id))

    @json_parse
    def get_net_by_id(self, net_id):
        """Get network by id.

        :param net_id: type string, instance id.
        :return dictionary
        """
        return self.client.get(
            '/virtual-network/{0}'.format(net_id))

    @json_parse
    def get_bgp_routers(self):
        """Get bgp routers."""
        return self.client.get('/bgp-routers')

    @json_parse
    def get_bgp_by_id(self, bgp_id):
        """Get bgp router by id.

        :param bgp_id: type string, bgp router id.
        :return dictionary
        """
        return self.client.get('/bgp-router/{0}'.format(bgp_id))
