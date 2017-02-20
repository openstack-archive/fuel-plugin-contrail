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
import ssl
import string
import time
from random import choice

from devops.helpers.helpers import tcp_ping
from devops.helpers.helpers import wait
from devops.helpers.ssh_client import SSHAuth

from fuelweb_test import logger
from fuelweb_test.helpers import os_actions
from fuelweb_test.helpers.decorators import log_snapshot_after_test
from fuelweb_test.tests.base_test_case import SetupEnvironment
from fuelweb_test.tests.base_test_case import TestBasic
from fuelweb_test.settings import CONTRAIL_PLUGIN_PACK_UB_PATH
from fuelweb_test.settings import SERVTEST_PASSWORD
from fuelweb_test.settings import SERVTEST_TENANT
from fuelweb_test.settings import SERVTEST_USERNAME
from fuelweb_test.settings import DISABLE_SSL
from fuelweb_test.settings import SSH_IMAGE_CREDENTIALS

from proboscis import test
from proboscis.asserts import assert_true
from proboscis.asserts import assert_equal
from proboscis import SkipTest

from helpers.contrail_client import ContrailClient
from helpers import vsrx
from helpers import plugin
from helpers import openstack
from helpers.settings import OSTF_RUN_TIMEOUT
from helpers.ssh import SSH
from tests.test_contrail_check import TestContrailCheck


@test(groups=["contrail_system_tests"])
class SystemTests(TestBasic):
    """System test suite.

    The goal of integration and system testing is to ensure that new or
    modified components of Fuel and MOS work effectively with
    Contrail API without gaps in dataflow.
    """

    pack_copy_path = '/var/www/nailgun/plugins/contrail-5.1'
    add_package = \
        '/var/www/nailgun/plugins/contrail-5.0/' \
        'repositories/ubuntu/contrail-setup*'
    ostf_msg = 'OSTF tests passed successfully.'
    cluster_id = ''
    pack_path = CONTRAIL_PLUGIN_PACK_UB_PATH
    CONTRAIL_DISTRIBUTION = os.environ.get('CONTRAIL_DISTRIBUTION')
    cirros_auth = SSHAuth(**SSH_IMAGE_CREDENTIALS)

    def ping_instance_from_instance(self, os_conn, node_name,
                                    ip_pair, ping_result=0):
        """Check network connectivity between instances by ping.

        :param os_conn: type object, openstack
        :param ip_pair: type list, pair floating ips of instances
        :param ping_result: type interger, exite code of command execution
        by default is 0
        """
        for ip_from in ip_pair:
            with self.fuel_web.get_ssh_for_node(node_name) as remote:
                for ip_to in ip_pair[ip_from]:
                    command = "ping -c 5 {0}".format(ip_to)
                    logger.info(
                        "Check connectin from {0} to {1}.".format(
                            ip_from, ip_to))
                    assert_true(
                        remote.execute_through_host(
                            hostname=ip_from,
                            cmd=command,
                            auth=self.cirros_auth)['exit_code'] == ping_result,
                        'Ping responce is not received.')

    def get_role(self, os_conn, role_name):
        """Get role by name."""
        role_list = os_conn.keystone.roles.list()
        for role in role_list:
            if role.name == role_name:
                return role
        return None

    def add_role_to_user(self, os_conn, user_name, role_name, tenant_name):
        """Assign role to user.

        :param os_conn: type object
        :param user_name: type string,
        :param role_name: type string
        :param tenant_name: type string
        """
        tenant_id = os_conn.get_tenant(tenant_name).id
        user_id = os_conn.get_user(user_name).id
        role_id = self.get_role(os_conn, role_name).id
        os_conn.keystone.roles.add_user_role(user_id, role_id, tenant_id)

    @test(depends_on=[SetupEnvironment.prepare_slaves_5],
          groups=["systest_setup"])
    @log_snapshot_after_test
    def systest_setup(self):
        """Setup for system test suite.

        Scenario:
            1. Create an environment with "Neutron with tunneling
               segmentation" as a network configuration
            2. Enable Contrail plugin
            3. Add 1 node with contrail-controller, contrail-analytic roles
            4. Add a node with controller, mongo roles
            5. Add a node with compute role
            6. Add a node contrail-analytics-db role
            7. Deploy cluster with plugin
            8. Run OSTF.

        Duration 90 min

        """
        self.show_step(1)
        plugin.prepare_contrail_plugin(
            self, slaves=5, options={'ceilometer': True})

        # activate vSRX image
        vsrx_setup_result = vsrx.activate()

        self.show_step(2)
        plugin.activate_plugin(self)

        plugin.show_range(self, 3, 7)
        self.fuel_web.update_nodes(
            self.cluster_id,
            {
                'slave-01': ['contrail-controller', 'contrail-analytics'],
                'slave-02': ['controller', 'mongo'],
                'slave-03': ['compute'],
                'slave-04': ['compute'],
                'slave-05': ['contrail-analytics-db'],
            })

        self.show_step(7)
        openstack.deploy_cluster(self)
        self.show_step(8)
        if vsrx_setup_result:
            self.fuel_web.run_ostf(
                cluster_id=self.cluster_id,
                test_sets=['smoke', 'sanity', 'tests_platform'],
                timeout=OSTF_RUN_TIMEOUT)
        TestContrailCheck(self).cloud_check(['contrail'])

        self.env.make_snapshot("systest_setup", is_make=True)

    @test(depends_on=[systest_setup],
          groups=["create_new_network_via_contrail"])
    @log_snapshot_after_test
    def create_new_network_via_contrail(self):
        """Create a new network via Contrail.

        Scenario:
            1. Setup systest_setup.
            2. Create a new network via Contrail API.
            3. Launch 2 new instance in the network with default security group
               via Horizon API.
            4. Check ping connectivity between instances.
            5. Verify on Contrail controller WebUI that network is there and
               VMs are attached to it.

        Duration: 15 min

        """
        # constants
        net_name = 'net_1'
        self.show_step(1)
        self.env.revert_snapshot('systest_setup')
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
                           "default-network-ipam"]}])['virtual-network']
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
            wait(
                lambda: tcp_ping(ip, 22), timeout=60, interval=5,
                timeout_msg="Node {0} is not accessible by SSH.".format(ip))
            fips.append(ip)

        self.show_step(4)
        ip_pair = dict.fromkeys(fips)
        for key in ip_pair:
            ip_pair[key] = [value for value in fips if key != value]
        controller = self.fuel_web.get_nailgun_primary_node(
            self.env.d_env.nodes().slaves[1])
        self.ping_instance_from_instance(os_conn, controller.name, ip_pair)

        self.show_step(5)
        net_info = contrail_client.get_net_by_id(
            network['uuid'])['virtual-network']
        net_interface_ids = []
        for interface in net_info['virtual_machine_interface_back_refs']:
            net_interface_ids.append(interface['uuid'])
        for instance in instances:
            interf_id = contrail_client.get_instance_by_id(
                instance.id)['virtual-machine'][
                    'virtual_machine_interface_back_refs'][0]['uuid']
            assert_true(
                interf_id in net_interface_ids,
                '{0} is not attached to network {1}'.format(
                    instance.name, net_name))

    @test(depends_on=[systest_setup],
          groups=["create_networks"])
    @log_snapshot_after_test
    def create_networks(self):
        """Create and terminate networks and verify in Contrail UI.

        Scenario:
            1. Setup systest_setup.
            2. Add 2 private networks via Horizon.
            3. Verify that networks are present in Contrail UI.
            4. Remove one of the private network via Horizon.
            5. Verify that the network is absent in Contrail UI.
            6. Add a private network via Horizon.
            7. Verify that all networks are present in Contrail UI.

        Duration: 15 min

        """
        # constants
        net_names = ['net_1', 'net_2']

        self.show_step(1)
        self.env.revert_snapshot('systest_setup')
        cluster_id = self.fuel_web.get_last_created_cluster()

        self.show_step(2)
        os_ip = self.fuel_web.get_public_vip(cluster_id)
        contrail_client = ContrailClient(os_ip)
        os_conn = os_actions.OpenStackActions(
            os_ip, SERVTEST_USERNAME,
            SERVTEST_PASSWORD,
            SERVTEST_TENANT)
        networks = []
        for net in net_names:
            logger.info('Create network {}'.format(net))
            network = os_conn.create_network(
                network_name=net)['network']
            networks.append(network)

        self.show_step(3)
        for net in networks:
            net_contrail = contrail_client.get_net_by_id(
                net['id'])['virtual-network']['uuid']
            assert_true(net['id'] == net_contrail)

        self.show_step(4)
        remove_net_id = networks.pop()['id']
        os_conn.neutron.delete_network(remove_net_id)

        self.show_step(5)
        contrail_networks = contrail_client.get_networks()['virtual-networks']
        assert_true(
            remove_net_id not in [net['uuid'] for net in contrail_networks])

        self.show_step(6)
        network = os_conn.create_network(
            network_name=net_names.pop())['network']
        networks.append(network)

        self.show_step(7)
        for net in networks:
            net_contrail = contrail_client.get_net_by_id(
                net['id'])['virtual-network']['uuid']
            assert_true(net['id'] == net_contrail)

    @test(depends_on=[systest_setup],
          groups=["contrail_vm_connection_in_different_tenants"])
    @log_snapshot_after_test
    def contrail_vm_connection_in_different_tenants(self):
        """Create a new network via Contrail.

        Scenario:
            1. Setup systest_setup.
            2. Create 1 new tenant(project).
            3. Create networks in the each tenants.
            4. Launch 2 new instance in different tenants(projects).
            5. Check ping connectivity between instances.
            6. Verify on Contrail controller WebUI that networks are there and
               VMs are attached to different networks.

        Duration: 15 min

        """
        # constants
        net_admin = 'net_1'
        net_test = 'net_2'
        cidr = '192.168.115.0'
        self.show_step(1)
        self.env.revert_snapshot('systest_setup')
        cluster_id = self.fuel_web.get_last_created_cluster()

        self.show_step(2)
        os_ip = self.fuel_web.get_public_vip(cluster_id)
        contrail_client = ContrailClient(os_ip)
        os_conn = os_actions.OpenStackActions(
            os_ip, SERVTEST_USERNAME,
            SERVTEST_PASSWORD,
            SERVTEST_TENANT)

        test_tenant = 'test'
        os_conn.create_user_and_tenant(test_tenant, test_tenant, test_tenant)
        self.add_role_to_user(os_conn, 'test', 'admin', 'test')

        test = os_actions.OpenStackActions(
            os_ip, test_tenant, test_tenant, test_tenant)
        test_contrail = ContrailClient(
            os_ip,
            credentials={
                'username': test_tenant,
                'tenant_name': test_tenant,
                'password': test_tenant})
        tenant = test.get_tenant(test_tenant)
        for user in os_conn.keystone.users.list():
            if user.name != test_tenant:
                tenant.add_user(user, self.get_role(test, 'admin'))

        self.show_step(3)
        logger.info(
            'Create network {0} in the {1}'.format(net_admin, tenant.name))
        network_test = test.create_network(
            network_name=net_test,
            tenant_id=tenant.id)['network']

        subnet_test = test.create_subnet(
            subnet_name=net_test,
            network_id=network_test['id'],
            cidr=cidr + '/24')

        router = test.create_router('router_1', tenant=tenant)
        test.add_router_interface(
            router_id=router["id"],
            subnet_id=subnet_test["id"])

        network = contrail_client.create_network([
            "default-domain", SERVTEST_TENANT, net_admin],
            [{"attr": {
                "ipam_subnets": [{
                    "subnet": {
                        "ip_prefix": '10.1.1.0',
                        "ip_prefix_len": 24}}]},
                    "to": ["default-domain",
                           "default-project",
                           "default-network-ipam"]}])['virtual-network']
        default_router = contrail_client.get_router_by_name(SERVTEST_TENANT)
        contrail_client.add_router_interface(network, default_router)

        self.show_step(4)
        srv_1 = os_conn.create_server_for_migration(
            neutron=True, label=net_admin)
        fip_1 = os_conn.assign_floating_ip(srv_1).ip
        wait(
            lambda: tcp_ping(fip_1, 22), timeout=60, interval=5,
            timeout_msg="Node {0} is not accessible by SSH.".format(fip_1))
        ip_1 = os_conn.get_nova_instance_ip(srv_1, net_name=net_admin)
        srv_2 = test.create_server_for_migration(
            neutron=True, label=net_test)
        srv_3 = test.create_server_for_migration(
            neutron=True, label=net_test)
        ips = []
        for srv in [srv_2, srv_3]:
            ip = (test.get_nova_instance_ip(srv, net_name=net_test))
            if ip_1 != ip_1:
                ips.append(ip)

        self.show_step(5)
        ip_pair = {}
        ip_pair[fip_1] = ips

        controller = self.fuel_web.get_nailgun_primary_node(
            self.env.d_env.nodes().slaves[1])
        self.ping_instance_from_instance(
            os_conn, controller.name, ip_pair, ping_result=1)

        self.show_step(6)
        logger.info('{}'.format(network))
        net_info = contrail_client.get_net_by_id(
            network['uuid'])['virtual-network']
        logger.info(''.format(net_info))
        net_interface_ids = []
        for interface in net_info['virtual_machine_interface_back_refs']:
            net_interface_ids.append(interface['uuid'])
        interf_id = contrail_client.get_instance_by_id(
            srv_1.id)['virtual-machine'][
                'virtual_machine_interface_back_refs'][0]['uuid']
        assert_true(
            interf_id in net_interface_ids,
            '{0} is not attached to network {1}'.format(
                srv_1.name, net_admin))
        net_info = test_contrail.get_net_by_id(
            network_test['id'])['virtual-network']
        net_interface_ids = []
        for interface in net_info['virtual_machine_interface_back_refs']:
            net_interface_ids.append(interface['uuid'])
        interf_id = test_contrail.get_instance_by_id(
            srv_2.id)['virtual-machine'][
                'virtual_machine_interface_back_refs'][0]['uuid']
        assert_true(
            interf_id in net_interface_ids,
            '{0} is not attached to network {1}'.format(
                srv_2.name, net_test))

    @test(depends_on=[systest_setup],
          groups=["contrail_ceilometer_metrics"])
    @log_snapshot_after_test
    def contrail_ceilometer_metrics(self):
        """Check that ceilometer collects contrail metrics.

        Scenario:
            1. Setup systest_setup.
            2. Create 2 instances in the default network.
            3. Send icpm packets from one instance to another.
            4. Check contrail ceilometer metrics:
                *ip.floating.receive.bytes
                *ip.floating.receive.packets
                *ip.floating.transmit.bytes
                *ip.floating.transmit.packets


        Duration 120 min

        """
        # constants
        ceilometer_metrics = [
            'ip.floating.receive.bytes',
            'ip.floating.receive.packets',
            'ip.floating.transmit.bytes',
            'ip.floating.transmit.packets']
        command = """source openrc; ceilometer sample-list -m {0}
         -q 'resource_id={1}'"""
        metric_type = 'cumulative'
        time_to_update_metrics = 60 * 10
        message = "Ceilometer doesn't collect metric {0}."

        self.show_step(1)
        self.env.revert_snapshot('systest_setup')
        self.show_step(2)
        cluster_id = self.fuel_web.get_last_created_cluster()
        os_ip = self.fuel_web.get_public_vip(cluster_id)
        os_conn = os_actions.OpenStackActions(
            os_ip, SERVTEST_USERNAME,
            SERVTEST_PASSWORD,
            SERVTEST_TENANT)

        srv_1 = os_conn.create_server_for_migration(
            neutron=True, label='admin_internal_net')
        fip_1 = os_conn.assign_floating_ip(srv_1)

        srv_2 = os_conn.create_server_for_migration(
            neutron=True, label='admin_internal_net')
        fip_2 = os_conn.assign_floating_ip(srv_2)

        for fip in [fip_1.ip, fip_2.ip]:
            wait(
                lambda: tcp_ping(fip, 22), timeout=60, interval=5,
                timeout_msg="Node {0} is not accessible by SSH.".format(fip))

        self.show_step(3)
        controller = self.fuel_web.get_nailgun_primary_node(
            self.env.d_env.nodes().slaves[1])
        self.ping_instance_from_instance(
            os_conn, controller.name, {fip_1.ip: [fip_2.ip]})

        self.show_step(4)
        with self.fuel_web.get_ssh_for_node("slave-02") as ssh:
            for metric in ceilometer_metrics:
                for resource_id in [fip_1.id, fip_2.id]:
                    wait(
                        lambda:
                        len(list(ssh.execute(
                            command.format(
                                metric, resource_id))['stdout'])) > 4,
                        timeout=time_to_update_metrics,
                        timeout_msg=message.format(metric))
                    m = list(ssh.execute(
                        command.format(metric, resource_id))['stdout'])
                    # Check type of metrics
                    collect_metric_type = m[3].split(' ')[5]
                    assert_true(
                        collect_metric_type == metric_type,
                        "Type of metric {0} not equel to {1}.".format(
                            collect_metric_type, metric_type))

    @test(depends_on=[systest_setup],
          groups=["https_tls_selected"])
    @log_snapshot_after_test
    def https_tls_selected(self):
        """Create a new network via Contrail.

        Scenario:
            1. Setup systest_setup.
            2. Get fingerprints from Openstack Horizon UI certificate
            3. Get fingerprints from Contrail UI certificate
            4. Get fingerprints from Contrail API certificate
            5. Verify that keys are identical


        Duration: 15 min

        """
        # constants
        if DISABLE_SSL:
            raise SkipTest()

        self.show_step(1)
        self.env.revert_snapshot('systest_setup')
        cluster_id = self.fuel_web.get_last_created_cluster()

        os_ip = self.fuel_web.get_public_vip(cluster_id)

        self.show_step(2)
        horizon_cert = ssl.get_server_certificate(
            (os_ip, 443), ssl_version=ssl.PROTOCOL_TLSv1)
        self.show_step(3)
        contrail_ui_cert = ssl.get_server_certificate(
            (os_ip, 8143), ssl_version=ssl.PROTOCOL_TLSv1)
        self.show_step(4)
        contrail_api_cert = ssl.get_server_certificate(
            (os_ip, 8082), ssl_version=ssl.PROTOCOL_TLSv1)
        self.show_step(5)
        if not horizon_cert == contrail_ui_cert:
            raise Exception("ContrailUI certificate is not valid")
        if not horizon_cert == contrail_api_cert:
            raise Exception("Contrail API certificate is not valid")

    @test(depends_on=[systest_setup],
          groups=["contrail_login_password"])
    @log_snapshot_after_test
    def contrail_login_password(self):
        """Create a new network via Contrail.

        Scenario:
            1. Setup systest_setup.
            2. Login as admin to Openstack Horizon UI.
            3. Create new user.
            4. Login as user to Openstack Horizon UI.
            5. Change login and password for user.
            6. Login to Openstack Horizon UI with new credentials.
            7. Login to Contrail Ui with same credentials.

        Duration: 15 min

        """
        # constants
        max_password_lengh = 64

        self.show_step(1)
        self.env.revert_snapshot('systest_setup')
        cluster_id = self.fuel_web.get_last_created_cluster()

        self.show_step(2)
        os_ip = self.fuel_web.get_public_vip(cluster_id)
        os_conn = os_actions.OpenStackActions(
            os_ip, SERVTEST_USERNAME,
            SERVTEST_PASSWORD,
            SERVTEST_TENANT)
        contrail_client = ContrailClient(os_ip)
        projects = contrail_client.get_projects()

        tenant = os_conn.get_tenant(SERVTEST_TENANT)

        self.show_step(3)
        chars = string.ascii_letters + string.digits + string.punctuation
        new_password = ''.join(
            [choice(chars) for i in range(max_password_lengh)])
        new_username = ''.join(
            [choice(chars) for i in range(max_password_lengh)])
        logger.info(
            'New username: {0}, new password: {1}'.format(
                new_username, new_password))
        new_user = os_conn.create_user(new_username, new_password, tenant)
        role = [role for role in os_conn.keystone.roles.list()
                if role.name == 'admin'].pop()
        os_conn.keystone.roles.add_user_role(new_user.id, role.id, tenant.id)

        self.show_step(4)
        os_actions.OpenStackActions(
            os_ip, new_username,
            new_password,
            SERVTEST_TENANT)

        self.show_step(5)
        new_password = ''.join(
            [choice(chars) for i in range(max_password_lengh)])
        new_user.manager.update_password(new_user, new_password)
        logger.info(
            'New username: {0}, new password: {1}'.format(
                new_username, new_password))
        time.sleep(30)  # need to update password for new user

        self.show_step(6)
        os_actions.OpenStackActions(
            os_ip, new_username,
            new_password,
            SERVTEST_TENANT)
        contrail = ContrailClient(
            os_ip,
            credentials={
                'username': new_username,
                'tenant_name': SERVTEST_TENANT,
                'password': new_password})

        assert_equal(
            projects, contrail.get_projects(),
            "Can not give info by Contrail API.")

    @test(depends_on=[systest_setup],
          groups=["contrail_public_connectivity_from_instance_without_fip"])
    @log_snapshot_after_test
    def contrail_public_connectivity_from_instance_without_fip(self):
        """Check network connectivity from instance without floating IP.

        Scenario:
            1. Setup systest_setup.
            2. Launch an instance using the default image, flavor and
               security group.
            3. Check that public IP 8.8.8.8 can be pinged from instance.
            4. Delete instance.

        Duration 5 min

        """
        self.show_step(1)
        self.env.revert_snapshot('systest_setup')
        net_name = 'admin_internal_net'
        cluster_id = self.fuel_web.get_last_created_cluster()
        os_ip = self.fuel_web.get_public_vip(cluster_id)
        os_conn = os_actions.OpenStackActions(
            os_ip, SERVTEST_USERNAME,
            SERVTEST_PASSWORD,
            SERVTEST_TENANT)

        self.show_step(2)

        # Launch instance as access point
        os_conn.goodbye_security()
        flavor = [
            f for f in os_conn.nova.flavors.list()
            if f.name == 'm1.micro'][0]
        image = os_conn.nova.images.list().pop()
        network = os_conn.nova.networks.find(label=net_name)
        access_point = os_conn.nova.servers.create(
            flavor=flavor, name='test1', image=image,
            nics=[{'net-id': network.id}]
        )
        wait(
            lambda: os_conn.get_instance_detail(
                access_point).status == 'ACTIVE',
            timeout=300)
        access_point_fip = os_conn.assign_floating_ip(access_point).ip
        wait(
            lambda: tcp_ping(access_point_fip, 22), timeout=120, interval=5,
            timeout_msg="Node {0} is not accessible by SSH.".format(
                access_point_fip))

        instance = os_conn.nova.servers.create(
            flavor=flavor, name='test2', image=image,
            nics=[{'net-id': network.id}]
        )
        wait(
            lambda: os_conn.get_instance_detail(
                instance).status == 'ACTIVE',
            timeout=300)

        self.show_step(3)
        # Get private ip of instance
        logger.info('{}'.format(os_conn.nova.servers.ips(instance.id)))
        ip = os_conn.nova.servers.ips(instance.id)[net_name].pop()['addr']
        with SSH(access_point_fip) as remote:
            remote.check_connection_through_host({ip: ['8.8.8.8']})

        self.show_step(4)
        for instance in [access_point, instance]:
            os_conn.delete_instance(instance)
            wait(
                lambda: os_conn.is_srv_deleted(instance),
                timeout=200, timeout_msg="Instance was not deleted.")
