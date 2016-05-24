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


from proboscis import test
from fuelweb_test import logger
from fuelweb_test.helpers import os_actions
from fuelweb_test.helpers.decorators import log_snapshot_after_test
from fuelweb_test.tests.base_test_case import SetupEnvironment
from fuelweb_test.tests.base_test_case import TestBasic
from helpers.contrail_client import ContrailClient
from fuelweb_test.settings import SERVTEST_PASSWORD
from fuelweb_test.settings import SERVTEST_TENANT
from fuelweb_test.settings import SERVTEST_USERNAME
from proboscis.asserts import assert_true
from helpers import plugin
from helpers import openstack


@test(groups=["plugins"])
class SystemTests(TestBasic):
    """System test suite.

    The goal of integration and system testing is to ensure that new or
    modified components of Fuel and MOS work effectively with
    Contrail API without gaps in dataflow.
    """

    def ping_instance_from_instance(self, ip_pair, ping_result=0):
        """Check network connectivity between instances by ping.

        :param ip_pair: type list, pair floating ips of instances
        :param ping_result: type interger, exite code of command execution
        by default is 0
        """
        creds = ("cirros", "cubswin:)")
        with self.fuel_web.get_ssh_for_node("slave-01") as ssh:
            for ip_from in ip_pair:
                for ip_to in ip_pair[ip_from]:
                    command = "ping -c 5 {0}".format(ip_to)
                    logger.info(
                        "Check connectin from {0} to {1}.".format(
                            ip_from, ip_to))
            ping = self.os_conn.execute_through_host(
                ssh, ip_from, command, creds)

            assert_true(ping['exit_code'] == ping_result, ping['stderr'])

    @test(depends_on=[SetupEnvironment.prepare_slaves_5],
          groups=["systest_setup"])
    @log_snapshot_after_test
    def systest_setup(self):
        """Setup for system test suite.

        Scenario:
            1. Create an environment with "Neutron with tunneling
               segmentation" as a network configuration
            2. Enable Contrail plugin
            3. Add 1 node with contrail-config, contrail-control and
               contrail-db roles
            4. Add a node with controller role
            5. Add a node with compute role
            6. Deploy cluster with plugin
            7. Run OSTF.
            8. Create snapshot sytest_setup.

        Duration 90 min

        """
        self.show_step(1)
        plugin.prepare_contrail_plugin(self, slaves=5)

        # activate vSRX image
        plugin.activate_vsrx()

        self.show_step(2)
        plugin.activate_plugin(self)

        plugin.show_range(self, 3, 6)
        self.fuel_web.update_nodes(
            self.cluster_id,
            {
                'slave-01': ['contrail-config',
                             'contrail-control',
                             'contrail-db'],
                'slave-02': ['controller'],
                'slave-03': ['compute'],
                'slave-04': ['compute'],
            })

        self.show_step(6)
        openstack.deploy_cluster(self)
        self.show_step(7)
        self.fuel_web.run_ostf(
            cluster_id=self.cluster_id, test_sets=['smoke'])

        self.show_step(8)
        self.env.make_snapshot("systest_setup", is_make=True)

    @test(depends_on=[systest_setup],
          groups=["create_new_network_via_contrail"])
    @log_snapshot_after_test
    def create_new_network_via_contrail(self):
        """Create a new network via Contrail.

        Scenario:
            1.Revert to snapshot systest_setup.
            2. Create a new network via Contrail API.
            3. Launch 2 new instance in the network with default security group
               via Horizon API.
            4. Check ping connectivity between instances.
            5. Verify on Contrail controller WebUI that network is there and
               VMs are attached to it.

        Duration: 15 min

        """
        net_name = 'net_1'
        self.show_step(1)
        self.env.revert_snapshot("systest_setup")

        cluster_id = self.fuel_web.get_last_created_cluster()

        self.show_step(2)
        os_ip = self.fuel_web.get_public_vip(cluster_id)
        contrail_client = ContrailClient(os_ip)
        network = contrail_client.create_network([
            "default-domain", SERVTEST_TENANT, net_name],
            [{"attr": {
                "ipam_subnets": [{
                    "subnet": {
                        "ip_prefix": '10.1.1.0',
                        "ip_prefix_len": 24}}]},
                    "to": ["default-domain",
                           "default-project",
                           "default-network-ipam"]}]
        )
        default_router = contrail_client.get_router_by_name(SERVTEST_TENANT)
        contrail_client.add_router_interface(network, default_router)

        self.show_step(3)
        os_conn = os_actions.OpenStackActions(
            os_ip, SERVTEST_USERNAME,
            SERVTEST_PASSWORD,
            SERVTEST_TENANT)

        hypervisors = os_conn.get_hypervisors()
        instances = []
        fips = []
        for hypervisor in hypervisors:
            instance = os_conn.create_server_for_migration(
                neutron=True,
                availability_zone="nova:{0}".format(
                    hypervisor.hypervisor_hostname),
                label=net_name
            )
            instances.append(instance)
            ip = os_conn.assign_floating_ip(instance).ip
            fips.append(ip)

        self.show_step(4)
        ip_pair = dict.fromkeys(fips)
        for key in ip_pair:
            ip_pair[key] = [value for value in fips if key != value]
        self.ping_instance_from_instance(ip_pair)

        self.show_step(5)
        net_info = contrail_client.get_net_by_id(network['uuid'])
        net_interface_ids = []
        for interface in net_info['virtual_machine_interface_back_refs']:
            net_interface_ids.append(interface['uuid'])
        for instance in instances:
            interf_id = contrail_client.get_instance_by_id(
                instance.id)['virtual_machine_interface_back_refs'][0]['uuid']
            assert_true(
                interf_id in net_interface_ids,
                '{0} is not attached to network {1}'.forma(
                    instance.name, net_name))
