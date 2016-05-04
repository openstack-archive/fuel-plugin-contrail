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
    pack_copy_path = '/var/www/nailgun/plugins/contrail-4.0'
    add_package = \
        '/var/www/nailgun/plugins/contrail-4.0/' \
        'repositories/ubuntu/contrail-setup*'

    cluster_id = ''

    pack_path = CONTRAIL_PLUGIN_PACK_UB_PATH

    CONTRAIL_DISTRIBUTION = os.environ.get('CONTRAIL_DISTRIBUTION')

    def get_network_templ(self, template_name):
        """Get netwok template.

        param: template_name: type string, name of file
        """
        template = 'doc/source/examples/{0}.yaml'.format(template_name)
        logger.info('{0}'.format(template))
        if os.path.exists(template):
            with open(template) as template_file:
                return yaml.load(template_file)
        else:
            raise Exception('Cannot find network template')

    @test(depends_on=[SetupEnvironment.prepare_slaves_5],
          groups=["contrail_net_template"])
    @log_snapshot_after_test
    def contrail_net_template(self):
        """Deploy cluster with Contrail plugin and network template.

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
            4. Set the ``render_addr_mask`` parameter to `internal`
               for this network by typing:
               fuel network-group --set --network 6 --meta
               '{"name": "private", "notation": "cidr", "render_type": null,
               "map_priority": 2, "configurable": true, "use_gateway": true,
               "render_addr_mask": "internal", "vlan_start": null,
               "cidr": "10.109.3.0/24"}'
            5. Save sample :download:
               `network template<examples/network_template_1.yaml>`
            6. Upload the network template by typing:
               fuel --env 1 network-template --upload --dir /root/
            7. Start deploy, pressing "Deploy changes" button.

        """
        plugin.prepare_contrail_plugin(self, slaves=5)

        # enable plugin in contrail settings
        plugin.activate_plugin(self)
        # activate vSRX image
        vsrx_setup_result = plugin.activate_vsrx()

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
        )

        plugin.show_range(self, 2, 5)
        plugin.net_group_preparation(self)

        self.show_step(5)
        network_template = self.get_network_templ('network_template_1')
        self.show_step(6)
        self.fuel_web.client.upload_network_template(
            cluster_id=self.cluster_id, network_template=network_template)

        self.show_step(7)
        openstack.deploy_cluster(self)

        # run OSTF tests
        if vsrx_setup_result:
            self.fuel_web.run_ostf(cluster_id=self.cluster_id)
