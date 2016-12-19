import pytest

from keystoneauth1.identity.v2 import Password
from keystoneauth1.session import Session

from vapor.settings import (
    KEYSTONE_CREDS, PATH_TO_CERT, VERIFY_SSL, DISABLE_SSL, CONTAIL_API_PORT)


class ContrailClient(object):
    """Contrail utilite wrapper."""

    def __init__(self, controller_node_ip, contrail_port=CONTAIL_API_PORT,
                 credentials=KEYSTONE_CREDS, **kwargs):
        """Create ContrailClient object."""
        print('[ContrailClient:__init__]')
        if DISABLE_SSL:

            self.url = "http://{0}:{1}".format(controller_node_ip,
                                               contrail_port)
            self.keystone_url = "http://{0}:5000/v2.0".format(
                controller_node_ip)
        else:
            self.url = "https://{0}:{1}".format(
                controller_node_ip, contrail_port)
            self.keystone_url = 'https://{0}:5000/v2.0/'.format(
                controller_node_ip)
            insecure = not VERIFY_SSL
            credentials.update({'ca_cert': PATH_TO_CERT, 'insecure': insecure})
        auth = Password(auth_url=self.keystone_url,
                        username=KEYSTONE_CREDS['username'],
                        password=KEYSTONE_CREDS['password'],
                        tenant_name=KEYSTONE_CREDS['tenant_name'])
        self._client = Session(auth=auth, verify=False)

    def __enter__(self):
        print('[ContrailClient:__enter__]')
        return self

    def __exit__(self, type, value, traceback):
        print('[ContrailClient:__exit__]')
        pass

    @property
    def client(self):
        """Client property."""
        return self._client

    def _get(self, data_path):
        """Get method."""
        print('[_get] url: %s' % str(self.url + data_path))
        return self.client.get(url=self.url + data_path).json()

    def _delete(self, data_path):
        """Delete method."""
        return self.client.delete(url=self.url + data_path).json()

    def _post(self, data_path, **kwargs):
        """Post method."""
        return self.client.post(
            url=self.url + data_path, connect_retries=1, **kwargs).json()

    def _put(self, data_path, **kwargs):
        """Put method."""
        return self.client.put(
            url=self.url + data_path, connect_retries=1, **kwargs).json()

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
        return self._post('/virtual-networks', json=data)

    def add_router_interface(self, network, route_table, attr=None):
        """Add router interface to network.

        :param network: type dictionary, network
        :param route_table: type dictionary, router
        :param attr: type dictionary, parameters of router interface(optianal)
        """
        data = {"virtual-network": {'fq_name': network['fq_name'],
                'route_table_refs': [{
                    'to': route_table['fq_name'], "attr":attr}]}}
        return self._put(
            '/virtual-network/{0}'.format(network['uuid']), json=data)

    def get_route_tables(self):
        """Get router."""
        return self._get('/route-tables')

    def get_networks(self):
        """Get networks."""
        return self._get('/virtual-networks')

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

    def get_projects(self):
        """Get router."""
        return self._get('/projects')

    def get_project_by_name(self, name):
        """Get project by name.

        :param name: type string, name of project.
        :return dictionary
        """
        projects = self.get_projects()
        project = [p for p in projects if name in p['fq_name']]
        return project.pop()

    def get_instance_by_id(self, instance_id):
        """Get instance by id.

        :param instance_id: type string, instance id.
        :return dictionary
        """
        return self._get('/virtual-machine/{0}'.format(instance_id))

    def get_net_by_id(self, net_id):
        """Get network by id.

        :param net_id: type string, instance id.
        :return dictionary
        """
        return self._get('/virtual-network/{0}'.format(net_id))

    def get_bgp_routers(self):
        """Get bgp routers."""
        return self._get('/bgp-routers')

    def get_bgp_by_id(self, bgp_id):
        """Get bgp router by id.

        :param bgp_id: type string, bgp router id.
        :return dictionary
        """
        return self._get('/bgp-router/{0}'.format(bgp_id))

