#    Copyright 2016 Mirantis, Inc.
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

import os
import yaml

from proboscis import test

from fuelweb_test import logger
from fuelweb_test.helpers.decorators import log_snapshot_after_test
from fuelweb_test.tests.base_test_case import SetupEnvironment
from fuelweb_test.tests.test_net_templates_base import TestNetworkTemplatesBase
from fuelweb_test.settings import CONTRAIL_PLUGIN_PACK_UB_PATH
from fuelweb_test.tests.base_test_case import TestBasic
from helpers import openstack
from helpers import plugin


@test(groups=["contrail_net_template"])
class TestNetworkTemplates(TestNetworkTemplatesBase, TestBasic):
    """TestNetworkTemplates."""

    # constants
    node_name = lambda self, name_node: self.fuel_web. \
        get_nailgun_node_by_name(name_node)['hostname']

    cluster_id = ''

    pack_path = CONTRAIL_PLUGIN_PACK_UB_PATH

    CONTRAIL_DISTRIBUTION = os.environ.get('CONTRAIL_DISTRIBUTION')

    def get_network_template(self, template_name):
        template = 'doc/source/examples/{0}.yaml'.format(template_name)
        logger.info('{0}'.format(template))
        if os.path.exists(template):
            with open(template) as template_file:
                return yaml.load(template_file)

    @test(depends_on=[SetupEnvironment.prepare_slaves_9],
          groups=["contrail_net_template"])
    @log_snapshot_after_test
    def contrail_net_template(self):
        """Deploy cluster with DVS plugin, Neutron, Ceph and network template

        Scenario:
            1. Configure interfaces
            2. Next we need to set gateway for private network with Fuel CLI:
            *   Login with ssh to Fuel master node.
            *   List existing network-groups
            fuel network-group --env 1
            3. Remove and create again network-group *private* to set a gateway
            fuel network-group --delete --network 5
            fuel network-group --create --name /
            private --cidr 10.109.3.0/24 --gateway 10.109.3.1 --nodegroup 1
            4. Set the ``render_addr_mask`` parameter to `internal` for this network by typing:
            fuel network-group --set --network 6 --meta '{"name": "private", "notation": "cidr", "render_type": null,
             "map_priority": 2, "configurable": true, "use_gateway": true, "render_addr_mask": "internal",
              "vlan_start": null, "cidr": "10.109.3.0/24"}'
            5. Save sample :download:`network template<examples/network_template_1.yaml>`
            6. Upload the network template by typing:
            fuel --env 1 network-template --upload --dir /root/
            7. Start deploy, pressing "Deploy changes" button.

        """

        plugin.prepare_contrail_plugin(self, slaves=9, net_template='netTemplate')

        # enable plugin in contrail settings
        plugin.activate_plugin(self)

        self.fuel_web.update_nodes(
            self.cluster_id,
            {
                'slave-01': ['controller'],
                'slave-02': ['compute'],
                'slave-03': ['contrail-config',
                             'contrail-control',
                             'contrail-db'],
                'slave-04': ['contrail-config',
                             'contrail-control',
                             'contrail-db'],
                'slave-05': ['contrail-config',
                             'contrail-control',
                             'contrail-db'],
            },
            update_interfaces=False
        )

        network_template = self.get_network_template('network_template_1')
        self.fuel_web.client.upload_network_template(
            cluster_id=self.cluster_id, network_template=network_template)
        networks = self.generate_networks_for_template(
            template=network_template,
            ip_network='10.200.0.0/16',
            ip_prefixlen='24')
        existing_networks = self.fuel_web.client.get_network_groups()
        networks = self.create_custom_networks(networks, existing_networks)

        logger.debug('Networks: {0}'.format(
            self.fuel_web.client.get_network_groups()))

        self.fuel_web.verify_network(self.cluster_id)

        openstack.deploy_cluster(self)

        self.fuel_web.verify_network(self.cluster_id)

        self.check_ipconfig_for_template(self.cluster_id, network_template,
                                         networks)
        self.check_services_networks(self.cluster_id, network_template)

        self.fuel_web.run_ostf(cluster_id=self.cluster_id,
                               test_sets=['smoke', 'sanity',
                                          'ha', 'tests_platform'],
                               should_fail=2,
                               failed_test_name=[('Check network connectivity '
                                                  'from instance via floating IP'),
                                                 ('Launch instance with file injection')])
        self.check_ipconfig_for_template(self.cluster_id, network_template,
                                         networks)

        self.check_services_networks(self.cluster_id, network_template)






