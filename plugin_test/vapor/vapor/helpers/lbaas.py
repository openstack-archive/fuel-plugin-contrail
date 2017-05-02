# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from hamcrest import (assert_that, equal_to, is_, is_not, contains,
                      has_entries, starts_with, has_length)  # noqa: H310
import requests
from stepler import base
from stepler.third_party import waiter

from vapor import settings


class LBaaSSteps(base.BaseSteps):
    """LBaaS steps."""

    def _check_presence(self, objs, list_method, expected_presence, timeout=0):
        def _check_presence():
            all_objs = list_method()
            matcher = is_
            if not expected_presence:
                matcher = is_not
            return waiter.expect_that(
                all_objs,
                matcher(
                    contains(*[has_entries(id=obj['id']) for obj in objs])))

        waiter.wait(_check_presence, timeout_seconds=timeout)

    def create_lb(self, name, subnet, **kwargs):
        """Create loadbalancer and wait it became to online."""
        loadbalancer = self._client.lbaas_loadbalancers.create(
            name=name, vip_subnet_id=subnet['id'], **kwargs)

        loadbalancer = self.check_lb_provisioning_status(
            loadbalancer, timeout=settings.LBAAS_ONLINE_TIMEOUT)

        return loadbalancer

    def delete_lbs(self, loadbalancers):
        """Delete loadbalancer and wait for deletion to be completed."""
        for loadbalancer in loadbalancers:
            self._client.lbaas_loadbalancers.delete(loadbalancer['id'])

        self.check_lbs_presence(
            loadbalancers, timeout=settings.LBAAS_DELETE_TIMEOUT)

    def check_lb_provisioning_status(self,
                                     loadbalancer,
                                     expected_status="ACTIVE",
                                     timeout=0):
        """Check that loadbalancer has expected provisioning status."""

        def _check_status():
            lb = self._client.lbaas_loadbalancers.get(loadbalancer['id'])
            waiter.expect_that(lb['provisioning_status'],
                               is_not(starts_with('PENDING_')))
            return lb

        loadbalancer = waiter.wait(_check_status, timeout_seconds=timeout)
        assert_that(loadbalancer['provisioning_status'],
                    equal_to(expected_status))
        return loadbalancer

    def check_lbs_presence(self,
                           loadbalancers,
                           expected_presence=True,
                           timeout=0):
        """Check that loadbalancer is present (or not)."""
        self._check_presence(
            loadbalancers,
            self._client.lbaas_loadbalancers.list,
            expected_presence,
            timeout=timeout)

    def cleanup_lbs(self, names):
        """Remove all loadbalancers by names list."""
        loadbalancers = []
        for name in names:
            for loadbalancer in self._client.lbaas_loadbalancers.find_all(
                    name=name):
                loadbalancers.append(loadbalancer)
                self._client.lbaas_loadbalancers.delete(loadbalancer['id'])

        self.check_lbs_presence(
            loadbalancers,
            expected_presence=False,
            timeout=settings.LBAAS_DELETE_TIMEOUT)

    def create_listener(self, name, loadbalancer, protocol, protocol_port,
                        **kwargs):
        """Create LBaaS listener."""
        listener = self._client.lbaas_listeners.create(
            name=name,
            loadbalancer_id=loadbalancer['id'],
            protocol=protocol,
            protocol_port=protocol_port,
            **kwargs)

        self.check_lb_provisioning_status(
            loadbalancer, timeout=settings.LBAAS_ONLINE_TIMEOUT)

        return listener

    def delete_listener(self, listener):
        """Delete LBaaS listener."""
        listener = self._client.lbaas_listeners.get(listener['id'])
        loadbalancers = listener['loadbalancers']
        self._client.lbaas_listeners.delete(listener['id'])
        for lb in loadbalancers:
            self.check_lb_provisioning_status(
                lb, timeout=settings.LBAAS_ONLINE_TIMEOUT)

    def cleanup_listeners(self, names):
        """Remove all listeners by names list."""
        for name in names:
            for listener in self._client.lbaas_listeners.find_all(name=name):
                self.delete_listener(listener)

    def create_pool(self, name, listener, protocol, lb_algorithm, **kwargs):
        """Create LBaaS pool."""
        pool = self._client.lbaas_pools.create(
            name=name,
            listener_id=listener['id'],
            protocol=protocol,
            lb_algorithm=lb_algorithm,
            **kwargs)

        for loadbalancer in pool['loadbalancers']:
            self.check_lb_provisioning_status(
                loadbalancer, timeout=settings.LBAAS_ONLINE_TIMEOUT)

        return pool

    def delete_pool(self, pool):
        """Create LBaaS pool."""
        self._client.lbaas_pools.delete(pool['id'])
        for loadbalancer in pool['loadbalancers']:
            self.check_lb_provisioning_status(
                loadbalancer, timeout=settings.LBAAS_ONLINE_TIMEOUT)

    def cleanup_pools(self, names):
        """Remove all pools by names list."""
        loadbalancers = []
        for name in names:
            for pool in self._client.lbaas_pools.find_all(name=name):
                self._client.lbaas_pools.delete(pool['id'])
                loadbalancers.extend(pool['loadbalancers'])

        for loadbalancer in loadbalancers:
            self.check_lb_provisioning_status(
                loadbalancer, timeout=settings.LBAAS_ONLINE_TIMEOUT)

    def create_member(self, pool, address, protocol_port, subnet, **kwargs):
        """Create LBaaS pool member."""
        member = pool.members.create(
            address=address,
            protocol_port=protocol_port,
            subnet_id=subnet['id'],
            **kwargs)

        for loadbalancer in pool['loadbalancers']:
            self.check_lb_provisioning_status(
                loadbalancer, timeout=settings.LBAAS_ONLINE_TIMEOUT)

        return member

    def delete_member(self, pool, member):
        """Delete LBaaS pool member."""
        pool.members.delete(member['id'])

        for loadbalancer in pool['loadbalancers']:
            self.check_lb_provisioning_status(
                loadbalancer, timeout=settings.LBAAS_ONLINE_TIMEOUT)

    def check_balancing(self, ip, port, expected_count):
        """Check that responses contains `expected_counts` variants."""
        responses = set()
        for _ in range(expected_count * 3):
            r = requests.get("http://{}:{}/".format(ip, port))
            r.raise_for_status()
            responses.add(r.text)
        assert_that(responses, has_length(expected_count))
