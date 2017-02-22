from . import base


class ContrailAnalyticsClient(base.ContrailBaseClient):
    """Contrail analytics client."""

    class MatchOps(object):
        # Query match operation constants
        EQUAL = 1
        NOT_EQUAL = 2
        IN_RANGE = 3
        NOT_IN_RANGE = 4  # not supported currently
        # following are only for numerical column fields
        LEQ = 5  # column value is less than or equal to filter value
        GEQ = 6  # column value is greater than or equal to filter value
        PREFIX = 7  # column value has the "value" field as prefix
        REGEX_MATCH = 8  # for filters only

    def get_alarms(self):
        """Get alarms."""
        return self._get('/analytics/alarms')

    def get_tables(self):
        """Return tables list."""
        return self._get('/analytics/tables')

    def get_table(self, table_name):
        """Return table information."""
        return self._get('/analytics/table/{}'.format(table_name))

    def get_table_schema(self, table_name):
        """Return table schema."""
        return self._get('/analytics/table/{}/schema'.format(table_name))

    def get_uves_generators(self):
        """Return uves generators names."""
        for generator in self._get('/analytics/uves/generators'):
            yield generator['name']

    def get_uves_generator_data(self, name):
        """Return uves generator data."""
        return self._get('/analytics/uves/generator/{}?flat'.format(name))

    def get_uves_vrouters(self):
        """Return uves vrouters names."""
        for generator in self._get('/analytics/uves/vrouters'):
            yield generator['name']

    def get_uves_vrouter_ops(self, hostname):
        """Return uves vrouter ops."""
        return self._get('/analytics/uves/vrouter/{}?flat'.format(hostname))

    def get_uves_control_nodes(self):
        """Return uves control nodes names."""
        for generator in self._get('/analytics/uves/control-nodes'):
            yield generator['name']

    def get_uves_control_node_ops(self, hostname):
        """Return uves control node ops."""
        return self._get('/analytics/uves/control-node/{}?flat'.format(
            hostname))

    def get_uves_analytics_nodes(self):
        """Return uves analytics nodes names."""
        for generator in self._get('/analytics/uves/analytics-nodes'):
            yield generator['name']

    def get_uves_analytics_node_ops(self, hostname):
        """Return uves analytics node ops."""
        return self._get('/analytics/uves/analytics-node/{}?flat'.format(
            hostname))

    def get_uves_config_nodes(self):
        """Return uves config nodes names."""
        for generator in self._get('/analytics/uves/config-nodes'):
            yield generator['name']

    def get_uves_config_node_ops(self, hostname):
        """Return uves config node ops."""
        return self._get('/analytics/uves/config-node/{}?flat'.format(
            hostname))

    def get_uves_bgp_peers(self):
        """Return uves config nodes names."""
        for generator in self._get('/analytics/uves/bgp-peers'):
            yield generator['name']

    def get_uves_bgp_peer_info(self, name):
        """Return uves config node ops."""
        return self._get('/analytics/uves/bgp-peer/{}?flat'.format(
            name))

    def database_purge(self, purge_input):
        """Send a request to purge database."""
        return self._post(
            '/analytics/operation/database-purge',
            json={'purge_input': purge_input})

    def post_query(self,
                   table,
                   start_time,
                   end_time,
                   select_fields,
                   where=None,
                   limit=1,
                   async=False):
        """Post a query to analytics.

        Example:
            client.post_query(
                table='StatTable.DatabasePurgeInfo.stats',
                start_time=1483000823697329,
                end_time='now-1m',
                select_fields=[
                    'stats.purge_id',
                    'stats.purge_status',
                    'stats.purge_status_details'
                ],
                where=[
                    [
                        {'name': 'stats.purge_id',
                         'value': purge_id,
                         'op': client.MatchOps.EQUAL},
                        # AND
                        {'name': 'stats.request_time',
                        'value': 1483000823697329,
                        'value2': 1483000823697330,
                        'op': client.MatchOps.IN_RANGE}
                    ],
                    # OR
                    [
                        {...},
                        # AND
                        {...},
                    ]
                ],
                limit=1))

        Args:
            table (str): Table name to make query
            start_time (int|str): Microseconds in UTC since Epoch or string
                value like 'now',  'now-5m'
            end_time (int|str): Same as `start_time`
            select_fields (list|tuple): List of field's names for return
            where (list, optional): List of lists of dicts to filter results
            limit (int, optional): Limit for results
            async (bool, optional): Make async query. In case True - this
                method returns a path to check query result.


        """
        where = where or []
        data = dict(
            table=table,
            start_time=start_time,
            end_time=end_time,
            select_fields=select_fields,
            where=where,
            limit=limit)
        headers = {}
        if async:
            headers = {'Expect': '202-accepted'}
        result = self._post('/analytics/query', json=data, headers=headers)
        if async:
            result = result['href']
        return result
