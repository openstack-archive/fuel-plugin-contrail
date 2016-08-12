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

from prettytable import PrettyTable

from proboscis.asserts import assert_true
from proboscis.asserts import assert_false

from devops.error import TimeoutError
from devops.helpers.helpers import tcp_ping
from devops.helpers.helpers import wait

from fuelweb_test import logger
from fuelweb_test.helpers import os_actions
from fuelweb_test.settings import SERVTEST_PASSWORD
from fuelweb_test.settings import SERVTEST_TENANT
from fuelweb_test.settings import SERVTEST_USERNAME

from helpers.ssh import SSH


class TestContrailCheck(object):
    """Test suite for contrail openstack check."""

    subnet_cidr = '192.168.112.0/24'
    net_name = 'contrail_check_net'
    router_name = 'contrail_check_router'
    image_name = 'contrail_check_image'

    def __init__(self, obj):
        """Create Test client for run tests.

        :param obj: Test case object
        """
        self.obj = obj
        self.node_roles = [
            role for node in self.obj.fuel_web.client.list_nodes()
            for role in node['roles']]
        cluster_id = self.obj.fuel_web.get_last_created_cluster()
        self.volume_ceph = self.obj.fuel_web.client.get_cluster_attributes(
            cluster_id)['editable']['storage']['volumes_ceph']['value']
        ip = self.obj.fuel_web.get_public_vip(cluster_id)
        self.os_conn = os_actions.OpenStackActions(
            ip, SERVTEST_USERNAME, SERVTEST_PASSWORD, SERVTEST_TENANT)

    def _get_tests(self, set_tests):
        """Get all callable tests of a class.

        :param: a list of test case types: sriov, dpdk
        :returns: a list of tuples of the form (test_name, test_method)
        """
        methods = inspect.getmembers(
            self,
            predicate=lambda x: inspect.ismethod(x) or inspect.isfunction(x))
        tests = []
        for t in set_tests:
            tests.extend([m for m in methods if t in m[0]])
        return tests

    def _run_tests(self, set_tests):
        """Run test cases of TestContrailCheck test suite.

        :param set_tests: a list of test case types: sriov, dpdk
        :returns: a list of dictionaries of form(test_name, test_result)
        """
        tests = self._get_tests(set_tests)
        results = {}
        for test_name, test_method in tests:
            try:
                logger.info('#### Run {0} ###'.format(test_name))
                test_method()
                results[test_name] = 'Passed'
            except Exception as exc:
                if exc.message == 'SkipTest':
                    logger.info('{0} skipped.'.format(test_name))
                    results[test_name] = 'Skipped'
                else:
                    logger.info('{0} failed with error {1}'.format(
                        test_name, exc))
                    results[test_name] = 'Failed'
            try:
                self._clear_openstack()
            except Exception as exc:
                logger.info('{0}'.format(exc))
        return results

    def _create_table_of_results(self, test_results):
        """Create table of test results.

        :param test_results: dictionary of test results
        """
        table = PrettyTable()
        table.field_names = ['Test', 'Result']
        for key in test_results:
            table.add_row([key, test_results[key]])
        table.align['Test'] = 'l'
        return table

    def cloud_check(self, set_tests, should_fail=None):
        """Run and check results of test cases of TestContrailCheck test suite.

        :param set_tests: list of test cases name
        :param set_tests: list of test cases name which should fail
                          according bug
        """
        test_result = self._run_tests(set_tests)
        logger.info('{0}'.format(self._create_table_of_results(test_result)))
        if should_fail:
            for failed_test in should_fail:
                test_result.pop(failed_test)
        assert_false(
            'Failed' in test_result.values(),
            'Following test cases have failed: {0}'.format(
                [r for r in test_result.keys()
                 if 'Failed' in test_result[r]]))

    def _clear_openstack(self):
        """Clear all created openstack objects during test case run."""
        self._remove_instances()
        # TODO(otsvigun) self._remove_floating_ips()
        self._remove_routers()
        self._remove_subnets()
        self._remove_network()
        self._remove_security_groups()
        self._remove_images()

    def _remove_network(self):
        """Remove network."""
        logger.info('Remove network.')
        network_id = self.os_conn.nova.networks.find(label=self.net_name).id
        if network_id:
            try:
                self.os_conn.neutron.delete_network(network_id)
            except Exception as exc:
                logger.info('Network was not deleted. {0}'.format(exc))

    def _remove_subnets(self):
        """Remove subnets."""
        logger.info('Remove subnets.')
        subnet_ids = [
            sub['id'] for sub in self.os_conn.neutron.list_subnets()['subnets']
            if sub['name'] == self.net_name]
        if subnet_ids:
            for subnet_id in subnet_ids:
                try:
                    self.os_conn.neutron.delete_subnet(subnet_id)
                except Exception as exc:
                    logger.info('Subnet was not deleted. {0}'.format(exc))

    def _remove_routers(self):
        """Remove routers."""
        logger.info('Remove routers.')
        router_ids = [
            router['id']
            for router in self.os_conn.neutron.list_routers()['routers']
            if router['name'] == self.router_name]
        subnet_ids = [
            sub['id'] for sub in self.os_conn.neutron.list_subnets()['subnets']
            if sub['name'] == self.net_name]
        if router_ids:
            for router in router_ids:
                try:
                    self.os_conn.neutron.remove_gateway_router(router)
                    if subnet_ids:
                        self.os_conn.neutron.remove_interface_router(
                            router, {"subnet_id": subnet_ids[0]})
                    self.os_conn.neutron.delete_router(router)
                except Exception as exc:
                    logger.info('Router was not deleted. {0}'.format(exc))

    def _remove_instances(self):
        """Remove instances."""
        logger.info('Remove instances.')
        instances = self.os_conn.get_servers()
        if instances:
            for instance in instances:
                try:
                    self.os_conn.delete_instance(instance)
                    assert_true(
                        self.os_conn.verify_srv_deleted(instance),
                        "Instance was not deleted.")
                except Exception as exc:
                    logger.info('Instance was not deleted. {0}'.format(exc))

    def _remove_security_groups(self):
        """Remove security groups."""
        logger.info('Remove security groups.')
        security_groups = [
            sg
            for sg
            in self.os_conn.neutron.list_security_groups()['security_groups']
            if sg['name'] != 'default']
        if security_groups:
            for group in security_groups:
                try:
                    self.os_conn.nova.security_groups.delete(group['id'])
                except Exception as exc:
                    logger.info(
                        'Security group {0} was not deleted. {1}'.format(
                            group['name'], exc))

    def _remove_floating_ips(self):
        """Remove floatig ips."""
        logger.info('Remove floatig ips.')
        floating_ips = self.os_conn.nova.floating_ips.list()
        if floating_ips:
            for fip in floating_ips:
                try:
                    self.os_conn.nova.floating_ips.delete(fip)
                except Exception as exc:
                    logger.info('Floating ip {0} was not deleted. {1}'.format(
                        fip, exc))

    def _remove_images(self):
        """Remove images."""
        logger.info('Remove image.')
        images = [
            image for image in self.os_conn.nova.images.list()
            if image.name == self.image_name]
        if images:
            for image in images:
                try:
                    self.os_conn.nova.images.delete(image.id)
                except Exception as exc:
                    logger.info('Image {0} was not deleted. {1}'.format(
                        image.name, exc))

    def test_dpdk_boot_snapshot_vm(self):
        """Launch instance, create snapshot, launch instance from snapshot.

        Scenario:
            1. Create no default network with subnet.
            2. Get existing flavor with hpgs.
            3. Launch an instance using the default image and flavor with hpgs
               in the hpgs availability zone.
            4. Make snapshot of the created instance.
            5. Delete the last created instance.
            6. Launch another instance from the snapshot created in step 4
               and flavor with hpgs in the hpgs availability zone.
            7. Delete the last created instance.

        Duration 5 min

        """
        az_name = 'hpgs'

        logger.info('Create no default network with subnet.')
        network = self.os_conn.create_network(
            network_name=self.net_name)['network']
        self.os_conn.create_subnet(
            subnet_name=self.net_name,
            network_id=network['id'],
            cidr=self.subnet_cidr,
            ip_version=4)

        logger.info('Get existing flavor with hpgs.')
        flavor = [
            f for f in self.os_conn.nova.flavors.list()
            if az_name in f.name][0]

        logger.info("""Launch an instance using the default image and
         flavor with hpgs in the hpgs availability zone.""")
        srv_1 = self.os_conn.create_server_for_migration(
            neutron=True, availability_zone=az_name,
            label=self.net_name, flavor=flavor)

        logger.info('Make snapshot of the created instance.')
        image = self.os_conn.nova.servers.create_image(srv_1, self.image_name)
        wait(lambda: self.os_conn.nova.images.get(image).status == 'ACTIVE',
             timeout=1800, timeout_msg='Image is not active.')

        logger.info('Delete the last created instance.')
        self.os_conn.delete_instance(srv_1)
        assert_true(
            self.os_conn.verify_srv_deleted(srv_1),
            "Instance was not deleted.")

        logger.info("""Launch another instance from the snapshot created
            in step 4 and flavor with hpgs in the hpgs availability zone.""")
        srv_2 = self.os_conn.nova.servers.create(
            flavor=flavor, name='srv_2', image=image,
            availability_zone=az_name, nics=[{'net-id': network['id']}])
        self._verify_instance_state(instances=[srv_2])

        logger.info('Delete the last created instance.')
        self.os_conn.delete_instance(srv_2)
        assert_true(
            self.os_conn.verify_srv_deleted(srv_2),
            "Instance was not deleted.")

    def test_dpdk_volume(self):
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
        if not (self.volume_ceph or 'cinder' in self.node_roles):
            raise Exception('SkipTest')
        else:
            az_name = 'hpgs'

            logger.info('Create no default network with subnet.')
            network = self.os_conn.create_network(
                network_name=self.net_name)['network']
            self.os_conn.create_subnet(
                subnet_name=self.net_name,
                network_id=network['id'],
                cidr=self.subnet_cidr,
                ip_version=4)

            logger.info('Get existing flavor with hpgs.')
            flavor = [
                f for f in self.os_conn.nova.flavors.list()
                if az_name in f.name][0]

            logger.info('Create a new small-size volume from image.')
            logger.info('Wait for volume status to become "available".')
            images_list = self.os_conn.nova.images.list()
            volume = self.os_conn.create_volume(image_id=images_list.pop().id)

            logger.info("""Launch an instance using the default image and
                flavor with hpgs in the hpgs availability zone.""")
            srv_1 = self.os_conn.create_server_for_migration(
                neutron=True, availability_zone=az_name,
                label=self.net_name, flavor=flavor,
                block_device_mapping={'vda': volume.id + ':::0'})

            logger.info('Wait for "Active" status.')
            self._verify_instance_state(instances=[srv_1])

            logger.info('Delete the last created instance.')
            self.os_conn.delete_instance(srv_1)
            assert_true(
                self.os_conn.verify_srv_deleted(srv_1),
                "Instance was not deleted.")

            logger.info('Delete volume and verify that volume deleted.')
            self.os_conn.delete_volume_and_wait(volume)

    def test_dpdk_check_public_connectivity_from_instance(self):
        """Check network connectivity from instance via floating IP.

        Scenario:
            1. Create no default network with subnet.
            2. Create Router_01, set gateway and add interface
               to external network.
            3. Get existing flavor with hpgs.
            4. Create a new security group (if it doesn`t exist yet).
            5. Launch an instance using the default image and flavor with hpgs
               in the hpgs availability zone.
            6. Create a new floating IP.
            7. Assign the new floating IP to the instance.
            8. Check connectivity to the floating IP using ping command.
            9. Check that public IP 8.8.8.8 can be pinged from instance.
            10. Delete instance.

        Duration 5 min

        """
        az_name = 'hpgs'
        ping_command = "ping -c 5 8.8.8.8"

        logger.info('Create no default network with subnet.')
        network = self.os_conn.create_network(
            network_name=self.net_name)['network']
        subnet = self.os_conn.create_subnet(
            subnet_name=self.net_name,
            network_id=network['id'],
            cidr=self.subnet_cidr,
            ip_version=4)

        logger.info("""Create Router_01, set gateway and add interface
               to external network.""")
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

        logger.info("Get existing flavor with hpgs.")
        flavor = [
            f for f in self.os_conn.nova.flavors.list()
            if az_name in f.name][0]

        logger.info("""Launch an instance using the default image and flavor
            with hpgs in the hpgs availability zone.""")
        srv = self.os_conn.create_server_for_migration(
            neutron=True, availability_zone=az_name,
            label=self.net_name, flavor=flavor)

        logger.info("Create a new floating IP.")
        logger.info("Assign the new floating IP to the instance.")
        fip = self.os_conn.assign_floating_ip(srv).ip

        logger.info(
            "Check connectivity to the floating IP using ping command.")
        wait(
            lambda: tcp_ping(fip, 22), timeout=120, interval=5,
            timeout_msg="Node {0} is not accessible by SSH.".format(fip))

        logger.info(
            "Check that public IP 8.8.8.8 can be pinged from instance.")
        with SSH(fip) as remote:
            result = remote.execute(ping_command)
            assert_true(result['exit_code'] == 0, result['stderr'])

        logger.info("Delete instance.")
        self.os_conn.delete_instance(srv)
        assert_true(
            self.os_conn.verify_srv_deleted(srv),
            "Instance was not deleted.")

    def test_sriov_boot_snapshot_vm(self):
        """Launch instance, create snapshot, launch instance from snapshot.

        Scenario:
            1. Create physical network.
            2. Create a subnet.
            3. Create a port.
            4. Boot the instance with the port on the SRIOV host.
            5. Create snapshot of instance.
            6. Delete the instance created in step 5.
            7. Launch instance from snapshot.
            8. Delete the instance created in step 7.

        Duration 5 min

        """
        binding_port = 'direct'

        logger.info('Create physical network.')
        body = {
            'network': {
                'name': self.net_name,
                'provider:physical_network': 'physnet1',
                'provider:segmentation_id': '5'}}
        network = self.os_conn.neutron.create_network(body)['network']

        logger.info('Create a subnet.')
        self.os_conn.create_subnet(
            subnet_name=self.net_name,
            network_id=network['id'],
            cidr=self.subnet_cidr,
            ip_version=4)

        logger.info('Create a port.')
        port = self.os_conn.neutron.create_port(
            {"port": {
                "network_id": network['id'],
                "binding:vnic_type": binding_port}})['port']

        logger.info('Boot the instance with the port on the SRIOV host.')
        images_list = self.os_conn.nova.images.list()
        flavors = self.os_conn.nova.flavors.list()
        flavor = [f for f in flavors if f.name == 'm1.micro'][0]

        srv_1 = self.os_conn.nova.servers.create(
            flavor=flavor, name='test1',
            image=images_list[0], nics=[{'port-id': port['id']}])

        self._verify_instance_state(instances=[srv_1])

        logger.info('Create snapshot of instance.')
        image = self.os_conn.nova.servers.create_image(srv_1, self.image_name)
        wait(lambda: self.os_conn.nova.images.get(image).status == 'ACTIVE',
             timeout=300, timeout_msg='Image is not active.')

        logger.info('Delete the instance created in step 5.')
        self.os_conn.delete_instance(srv_1)
        assert_true(
            self.os_conn.verify_srv_deleted(srv_1),
            "Instance was not deleted.")

        logger.info('Launch instance from snapshot.')
        port = self.os_conn.neutron.create_port(
            {"port": {
                "network_id": network['id'],
                "binding:vnic_type": binding_port}})['port']

        srv_2 = self.os_conn.nova.servers.create(
            flavor=flavor, name='test1',
            image=image, nics=[{'port-id': port['id']}])
        self._verify_instance_state(instances=[srv_2])

        logger.info('Delete the instance created in step 7.')
        self.os_conn.delete_instance(srv_2)
        assert_true(
            self.os_conn.verify_srv_deleted(srv_2),
            "Instance was not deleted.")

    def test_sriov_volume(self):
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
        if not (self.volume_ceph or 'cinder' in self.node_roles):
            raise Exception('SkipTest')
        else:
            binding_port = 'direct'

            logger.info('Create physical network.')
            body = {
                'network': {
                    'name': self.net_name,
                    'provider:physical_network': 'physnet1',
                    'provider:segmentation_id': '5'}}
            network = self.os_conn.neutron.create_network(body)['network']

            logger.info('Create a subnet.')
            self.os_conn.create_subnet(
                subnet_name=self.net_name,
                network_id=network['id'],
                cidr=self.subnet_cidr,
                ip_version=4)

            logger.info('Create a port.')

            port = self.os_conn.neutron.create_port(
                {"port": {
                    "network_id": network['id'],
                    "binding:vnic_type": binding_port}})['port']

            logger.info('Create a new small-size volume from image.')
            logger.info('Wait for volume status to become "available".')
            images_list = self.os_conn.nova.images.list()
            flavors = self.os_conn.nova.flavors.list()
            flavor = [f for f in flavors if f.name == 'm1.micro'][0]
            volume = self.os_conn.create_volume(image_id=images_list[0].id)

            logger.info("""Launch instance from created volume and port on
                the SRIOV host.""")
            srv_1 = self.os_conn.nova.servers.create(
                flavor=flavor, name='test1',
                image=images_list.pop(),
                block_device_mapping={'vda': volume.id + ':::0'},
                nics=[{'port-id': port['id']}])

            logger.info('Wait for "Active" status.')
            self._verify_instance_state(instances=[srv_1])

            logger.info('Delete instance.')
            self.os_conn.delete_instance(srv_1)
            assert_true(self.os_conn.verify_srv_deleted(srv_1),
                        "Instance was not deleted.")

            logger.info('Delete volume and verify that volume deleted.')
            self.os_conn.delete_volume_and_wait(volume)

    def _verify_instance_state(self, instances=None,
                               expected_state='ACTIVE', boot_timeout=400):
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

    def test_contrail_node_status(self):
        """Check contrail nodes for their status."""
        cluster_id = self.obj.fuel_web.get_last_created_cluster()
        logger.info('Check contrail node for cluster {}'.format(cluster_id))
        contrail_node_roles = {
            'contrail-config',
            'contrail-control',
            'contrail-db',
            'contrail-analytics'
        }

        def check_status(host_name):
            # command = "contrail-status | grep contrail| 'awk {print $2}'"
            command = "contrail-status | grep contrail"
            with self.obj.fuel_web.get_ssh_for_node(host_name) as remote:
                out = remote.execute(command)['stdout']
                for res in out:
                    logger.info('Check status: {}'.format(res))
                    assert('active' in res,
                           "Contrail node status invalid: {}".format(out))
            return True

        nailgun_nodes = self.obj.fuel_web.client.list_cluster_nodes(cluster_id)
        logger.info(
            'Nailgun nodes 1: {}'.format([n['name'] for n in nailgun_nodes]))

        nailgun_nodes = [node for node in nailgun_nodes
                         if not node['pending_addition'] and
                         set(node['roles']) & contrail_node_roles]

        logger.info(
            'Nailgun nodes 2: {}'.format([n['name'] for n in nailgun_nodes]))

        devops_nodes = self.obj.fuel_web.get_devops_nodes_by_nailgun_nodes(
            nailgun_nodes)

        for node in devops_nodes:
            logger.info("Check contrail status for node {}".format(node.name))
            check_status(node.name)
