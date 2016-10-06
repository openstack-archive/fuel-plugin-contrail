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
from fuelweb_test import logger


def update_cluster_settings(test_obj, cluster_id, section, attrs):
    """Update settings for parameter of the cluster

    :param test_obj: TestCase object
    :param cluster_id: Cluster identifier
    :param section: string
    :param attrs: dict - settings for the plugin
    :return: None
    """
    curr_attrs = test_obj.fuel_web.client.get_cluster_attributes(cluster_id)
    for option, value in attrs.iteritems():
        curr_attrs['editable'][section][option]['value'] = value
    test_obj.fuel_web.client.update_cluster_attributes(cluster_id, curr_attrs)


def get_cluster_settings(test_obj, cluster_id, section=''):
    """Get settings for parameter of the cluster

    :param test_obj: TestCase object
    :param cluster_id: Cluster identifier
    :param section: string
    :return: dict current cluster attributes values
    """
    attrs = test_obj.fuel_web.client.get_cluster_attributes(cluster_id)
    logger.info('Cluster {0} attrs: {1}'.format(cluster_id, attrs))
    if section:
        return attrs['editable'].get(section, {})
    return attrs['editable']
