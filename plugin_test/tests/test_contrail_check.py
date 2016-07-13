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

import inspect
from fuelweb_test import logger
from proboscis.asserts import assert_true
from proboscis.asserts import assert_false
from proboscis import SkipTest
from devops.error import TimeoutError
from devops.helpers.helpers import tcp_ping
from devops.helpers.helpers import wait
from fuelweb_test.helpers import os_actions
from fuelweb_test.settings import SERVTEST_PASSWORD
from fuelweb_test.settings import SERVTEST_TENANT
from fuelweb_test.settings import SERVTEST_USERNAME
from helpers import plugin


class TestContrailCheck(object):
    """Test suite for contrail openstack checkers."""

    subnet_cidr = '192.168.112.0/24'
    net_name = 'contrail_check'
    router_name = 'contrail_check'

    def __init__(self, obj):
        """Create Test client for run tests.

        :param obj: Test case object
        """
        self.obj = obj
        self.node_roles = [
            role for node in self.obj.fuel_web.client.list_nodes()
            for role in node['roles']]
        cluster_id = self.obj.fuel_web.get_last_created_cluster()
        ip = self.obj.fuel_web.get_public_vip(cluster_id)
        self.os_conn = os_actions.OpenStackActions(
            ip, SERVTEST_USERNAME, SERVTEST_PASSWORD, SERVTEST_TENANT)
        super(TestContrailCheck, self).__init__()

    def _get_tests(cls, set_tests=None):
        """Get all callable tests of a class.

        :returns: a list of tuples of the form (test_name, test_method)
        """
        methods = inspect.getmembers(
            cls,
            predicate=lambda x: inspect.ismethod(x) or inspect.isfunction(x))
        tests = []
        for t in set_tests:
            tests.extend([m for m in methods if t in m[0]])
        return tests

    def _run_tests(self, set_tests):
        """Run test cases of TestContrailCheck test suite.

        :param set_tests: list of test cases name
        """
        tests = self._get_tests(set_tests)
        results = {}
        logger.info('{0}'.format(tests))
        for test_name, test_method in tests:
            try:
                logger.info('Run {0}'.format(test_name))
                test_method()
                results[test_name] = 'Passed'
            except Exception as exc:
                logger.info('{0} failed with error {1}'.format(
                    test_name, exc))
                results[test_name] = ['Failed', exc]
            try:
                self._clear_openstack()
            except Exception as exc:
                logger.info('{0}'.format(exc))
        return results

    def cloud_check(self, set_tests, should_fail=None):
        """Run and check results of test cases of TestContrailCheck test suite.

        :param set_tests: list of test cases name
        :param set_tests: list of test cases name which should fail
                          according bug
        """
        test_result = self._run_tests(set_tests)
        if should_fail:
            for failed_test in should_fail:
                test_result.pop(failed_test)
        assert_false(
            'Failed' in test_result.values(),
            'Following  contrail check cloud test have failed: {0}'.format(
                [r for r in test_result.keys()
                 if 'Failed' in test_result[r]]))

    def _clear_openstack(self):
        """Clear all created openstack objects during test case run."""
        network_id = self.os_conn.nova.networks.find(label=self.net_name).id
        subnet_ids = [
            sub['id'] for sub in self.os_conn.neutron.list_subnets()['subnets']
            if sub['name'] == self.net_name]
        instances = self.os_conn.get_servers()
        security_groups = [
            sg
            for sg
            in self.os_conn.neutron.list_security_groups()['security_groups']
            if sg['name'] != 'default']

        router_ids = [
            router['id']
            for router in self.os_conn.neutron.list_routers()['routers']
            if router['name'] == self.router_name]
        for instance in instances:
            try:
                self.os_conn.delete_instance(instance)
            except Exception as exc:
                logger.info('Instance was not deleted. {0}'.format(exc))
        for router in router_ids:
            try:
                self.neutron_client.remove_gateway_router(router)
                if subnet_ids:
                    self.os_conn.neutron_client.remove_interface_router(
                        router, {"subnet_id": subnet_ids[0]})
                self.os_conn.neutron_client.delete_router(router)
            except Exception as exc:
                logger.info('Router was not deleted. {0}'.format(exc))
        for subnet_id in subnet_ids:
            try:
                self.os_conn.neutron_client.delete_subnet(subnet_id)
            except Exception as exc:
                logger.info('Subnet was not deleted. {0}'.format(exc))
        if network_id:
            try:
                self.os_conn.neutron.delete_network(network_id)
            except Exception as exc:
                logger.info('Network was not deleted. {0}'.format(exc))
        for group in security_groups:
            try:
                security_groups.delete(group)
            except Exception as exc:
                logger.info('Security group was not deleted. {0}'.format(
                    exc))

    def test_contrail_dpdk_boot_snapshot_vm(self):
        """Launch instance, create snapshot, launch instance from snapshot.

        Scenario:
            1. Create no default network with subnet.
            2. Get existing flavor with hpgs.
            3. Launch an instance using the default image and flavor with hpgs
               in the hpgs availability zone.
            4. Make snapshot of the created instance.
            5. Delete the last created instance.
            6. Launch another instance from the snapshot created in step 5.
               and flavor with hpgs in the hpgs availability zone.
            7. Delete the last created instance.

        Duration 5 min

        """
        az_name = 'hpgs'
        network = self.os_conn.create_network(
            network_name=self.net_name)['network']
        self.os_conn.create_subnet(
            subnet_name=self.net_name,
            network_id=network['id'],
            cidr=self.subnet_cidr,
            ip_version=4)

        self.obj.show_step(3)
        flavor = [
            f for f in self.os_conn.nova.flavors.list()
            if az_name in f.name][0]

        self.obj.show_step(4)
        srv_1 = self.os_conn.create_server_for_migration(
            neutron=True, availability_zone=az_name,
            label=self.net_name, flavor=flavor)

        self.obj.show_step(5)
        image = self.os_conn.nova.servers.create_image(srv_1, 'image1')
        wait(lambda: self.os_conn.nova.images.get(image).status == 'ACTIVE',
             timeout=300, timeout_msg='Image is not active.')

        self.obj.show_step(6)
        self.os_conn.delete_instance(srv_1)
        assert_true(
            self.os_conn.verify_srv_deleted(srv_1),
            "Instance was not deleted.")

        self.obj.show_step(7)
        srv_2 = self.os_conn.nova.servers.create(
            flavor=flavor, name='srv_2', image=image,
            availability_zone=az_name, nics=[{'net-id': network['id']}])
        self.verify_instance_state(instances=[srv_2])

        self.obj.show_step(8)
        self.os_conn.delete_instance(srv_2)
        assert_true(
            self.os_conn.verify_srv_deleted(srv_2),
            "Instance was not deleted.")

    def test_contrail_dpdk_volume(self):
        """Create volume and boot instance from it.

        Scenario:
            1. Create no default network with subnet.
            2. Get existing flavor with hpgs.
            3. Create a new small-size volume from image.
            4. Wait for volume status to become "available".
            5. Launch an instance using the default image and flavor with hpgs
               in the hpgs availability zone.
            6. Wait for "Active" status.
            7. Delete the last created instance.
            8. Delete volume and verify that volume deleted.

        Duration 5 min

        """
        if 'cinder' not in self.node_roles:
            raise SkipTest()
        az_name = 'hpgs'

        self.obj.show_step(2)
        network = self.os_conn.create_network(
            network_name=self.net_name)['network']
        self.os_conn.create_subnet(
            subnet_name=self.net_name,
            network_id=network['id'],
            cidr=self.subnet_cidr,
            ip_version=4)

        self.obj.show_step(3)
        flavor = [
            f for f in self.os_conn.nova.flavors.list()
            if az_name in f.name][0]

        plugin.show_range(self, 4, 6)
        images_list = self.os_conn.nova.images.list()
        volume = self.os_conn.create_volume(image_id=images_list[0].id)

        self.obj.show_step(6)
        srv_1 = self.os_conn.create_server_for_migration(
            neutron=True, availability_zone=az_name,
            label=self.net_name, flavor=flavor,
            block_device_mapping={'vda': volume.id + ':::0'})

        self.obj.show_step(7)
        self.verify_instance_state(instances=[srv_1])

        self.obj.show_step(8)
        self.os_conn.delete_instance(srv_1)
        assert_true(
            self.os_conn.verify_srv_deleted(srv_1),
            "Instance was not deleted.")

        self.obj.show_step(9)
        self.os_conn.delete_volume_and_wait(volume)

    def test_contrail_dpdk_check_public_connectivity_from_instance(self):
        """Check network connectivity from instance via floating IP.

        Scenario:
            2. Create no default network with subnet.
            3. Create Router_01, set gateway and add interface
               to external network.
            4. Get existing flavor with hpgs.
            5. Create a new security group (if it doesn`t exist yet).
            6. Launch an instance using the default image and flavor with hpgs
               in the hpgs availability zone.
            7. Create a new floating IP.
            8. Assign the new floating IP to the instance.
            9. Check connectivity to the floating IP using ping command.
            10. Check that public IP 8.8.8.8 can be pinged from instance.
            11. Delete instance.

        Duration 5 min

        """
        az_name = 'hpgs'
        ping_command = "ping -c 5 8.8.8.8"

        self.obj.show_step(2)
        network = self.os_conn.create_network(
            network_name=self.net_name)['network']
        subnet = self.os_conn.create_subnet(
            subnet_name=self.net_name,
            network_id=network['id'],
            cidr=self.subnet_cidr,
            ip_version=4)

        self.obj.show_step(3)
        gateway = {
            "network_id": self.os_conn.get_network('admin_floating_net')['id'],
            "enable_snat": True}
        router_param = {'router': {
            'name': self.router_name, 'external_gateway_info': gateway}}
        router = self.os_conn.neutron.create_router(
            body=router_param)['router']
        self.os_conn.add_router_interface(
            router_id=router["id"],
            subnet_id=subnet["id"])

        self.obj.show_step(4)
        flavor = [
            f for f in self.os_conn.nova.flavors.list()
            if az_name in f.name][0]

        plugin.show_range(self, 5, 7)
        srv = self.os_conn.create_server_for_migration(
            neutron=True, availability_zone=az_name,
            label=self.net_name, flavor=flavor)

        plugin.show_range(self, 7, 9)
        fip = self.os_conn.assign_floating_ip(srv).ip

        self.obj.show_step(9)
        wait(
            lambda: tcp_ping(fip, 22), timeout=120, interval=5,
            timeout_msg="Node {0} is not accessible by SSH.".format(fip))

        self.obj.show_step(10)
        with self.fuel_web.get_ssh_for_node("slave-01") as remote:
            assert_true(
                self.os_conn.execute_through_host(
                    remote, fip, ping_command)['exit_code'] == 0,
                'Ping responce is not received.')

        self.obj.show_step(11)
        self.os_conn.delete_instance(srv)
        assert_true(
            self.os_conn.verify_srv_deleted(srv),
            "Instance was not deleted.")

    def contrail_sriov_boot_snapshot_vm(self):
        """Launch instance, create snapshot, launch instance from snapshot.

        Scenario:
            1. Create physical network.
            2. Create a subnet.
            3. Create a port.
            4. Boot the instance with the port on the SRIOV host.
            5. Create snapshot of instance.
            6. Delete the instance created in step 5.
            7. Launch instance from snapshot.
            8. Delete the instance created in step 8.

        Duration 5 min

        """
        binding_port = 'direct'

        self.obj.show_step(2)
        body = {
            'network': {
                'name': self.net_name,
                'provider:physical_network': 'physnet1',
                'provider:segmentation_id': '5'}}
        network = self.os_conn.neutron.create_network(body)['network']

        self.obj.show_step(3)
        self.os_conn.create_subnet(
            subnet_name=self.net_name,
            network_id=network['id'],
            cidr=self.subnet_cidr,
            ip_version=4)

        self.obj.show_step(4)

        port = self.os_conn.neutron.create_port(
            {"port": {
                "network_id": network['id'],
                "binding:vnic_type": binding_port}})['port']

        self.obj.show_step(5)
        images_list = self.os_conn.nova.images.list()
        flavors = self.os_conn.nova.flavors.list()
        flavor = [f for f in flavors if f.name == 'm1.micro'][0]

        srv_1 = self.os_conn.nova.servers.create(
            flavor=flavor, name='test1',
            image=images_list[0], nics=[{'port-id': port['id']}])

        self._verify_instance_state(self.os_conn)

        self.obj.show_step(6)
        image = self.os_conn.nova.servers.create_image(srv_1, 'image1')
        wait(lambda: self.os_conn.nova.images.get(image).status == 'ACTIVE',
             timeout=300, timeout_msg='Image is not active.')

        self.obj.show_step(7)
        self.os_conn.delete_instance(srv_1)
        assert_true(
            self.os_conn.verify_srv_deleted(srv_1),
            "Instance was not deleted.")

        self.obj.show_step(8)
        port = self.os_conn.neutron.create_port(
            {"port": {
                "network_id": network['id'],
                "binding:vnic_type": binding_port}})['port']

        srv_2 = self.os_conn.nova.servers.create(
            flavor=flavor, name='test1',
            image=image, nics=[{'port-id': port['id']}])
        self._verify_instance_state(self.os_conn, instances=[srv_2])

        self.obj.show_step(9)
        self.os_conn.delete_instance(srv_2)
        assert_true(
            self.os_conn.verify_srv_deleted(srv_2),
            "Instance was not deleted.")

    def contrail_sriov_volume(self):
        """Create volume and boot instance from it.

        Scenario:
            1. Create physical network.
            2. Create a subnet.
            3. Create a port.
            4. Create a new small-size volume from image.
            5. Wait for volume status to become "available".
            6. Launch instance from created volume and port on the SRIOV host.
            7. Wait for "Active" status.
            8. Delete instance.
            9. Delete volume and verify that volume deleted.

        Duration 5 min

        """
        binding_port = 'direct'

        self.obj.show_step(2)
        body = {
            'network': {
                'name': self.net_name,
                'provider:physical_network': 'physnet1',
                'provider:segmentation_id': '5'}}
        network = self.os_conn.neutron.create_network(body)['network']

        self.obj.show_step(3)
        self.os_conn.create_subnet(
            subnet_name=self.net_name,
            network_id=network['id'],
            cidr=self.subnet_cidr,
            ip_version=4)

        self.obj.show_step(4)

        port = self.os_conn.neutron.create_port(
            {"port": {
                "network_id": network['id'],
                "binding:vnic_type": binding_port}})['port']

        plugin.show_range(self, 5, 7)
        images_list = self.os_conn.nova.images.list()
        flavors = self.os_conn.nova.flavors.list()
        flavor = [f for f in flavors if f.name == 'm1.micro'][0]
        volume = self.os_conn.create_volume(image_id=images_list[0].id)

        self.obj.show_step(7)
        srv_1 = self.os_conn.nova.servers.create(
            flavor=flavor, name='test1',
            image=images_list[0],
            block_device_mapping={'vda': volume.id + ':::0'},
            nics=[{'port-id': port['id']}])

        self.obj.show_step(8)
        self._verify_instance_state(self.os_conn, instances=[srv_1])

        self.obj.show_step(9)
        self.os_conn.delete_instance(srv_1)
        assert_true(self.os_conn.verify_srv_deleted(srv_1),
                    "Instance was not deleted.")

        self.obj.show_step(10)
        self.os_conn.delete_volume_and_wait(volume)

    def _verify_instance_state(self, instances=None,
                               expected_state='ACTIVE', boot_timeout=300):
        """Verify that current state of each instance/s is expected.

        :paramself.os_conn: type object, openstack
        :param instances: type list, list of created instances
        :param expected_state: type string, expected state of instance
        :param boot_timeout: type int, time in seconds to build instance
        """
        if not instances:
            instances = self.os_conn.nova.servers.list()
        for instance in instances:
            try:
                wait(
                    lambda: self.os_conn.get_instance_detail(
                        instance).status == expected_state,
                    timeout=boot_timeout)
            except TimeoutError:
                current_state = self.os_conn.get_instance_detail(
                    instance).status
                assert_true(
                    current_state == expected_state,
                    "Timeout is reached. Current state of {0} is {1}".format(
                        instance.name, current_state)
                )
