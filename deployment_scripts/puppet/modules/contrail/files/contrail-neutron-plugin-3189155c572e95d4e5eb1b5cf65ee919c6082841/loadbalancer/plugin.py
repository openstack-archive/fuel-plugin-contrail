#
# Copyright (c) 2014 Juniper Networks, Inc. All rights reserved.
#
from loadbalancer_db import LoadBalancerPluginDb
from neutron.openstack.common import log as logging
from neutron.plugins.common import constants
from neutron.services import service_base

from vnc_api.vnc_api import NoIdError

LOG = logging.getLogger(__name__)


class LoadBalancerPlugin(LoadBalancerPluginDb):
    supported_extension_aliases = ["lbaas"]

    def __init__(self):
        super(LoadBalancerPlugin, self).__init__()
        self._load_drivers()
        self._pool_driver = {}

    def _load_drivers(self):
        """Loads plugin-drivers specified in configuration."""
        self.drivers, self.default_provider = service_base.load_drivers(
            constants.LOADBALANCER, self)

    def get_plugin_description(self):
        return "OpenContrail LoadBalancer Service Plugin"

    def _pool_update_provider(self, context, pool):
        """ TODO: If the provider is specified in the request, verify
        that it is a valid value. Otherwise use default.
        """
        provider = self.default_provider
        pool['provider'] = provider
        return provider

    def _get_driver_for_provider(self, provider_name):
        return self.drivers[provider_name]

    def _get_driver_for_pool(self, pool_id):
        if not pool_id:
            return self.drivers[self.default_provider]
        if pool_id in self._pool_driver:
            return self._pool_driver[pool_id]
        try:
            pool = self._api.loadbalancer_pool_read(id=pool_id)
        except NoIdError:
            raise loadbalancer.PoolNotFound(pool_id=pool_id)
        provider_name = pool.get_loadbalancer_pool_provider()
        driver = self._get_driver_for_provider(provider_name)
        self._pool_driver[pool_id] = driver
        return driver

    def create_pool(self, context, pool):
        provider_name = self._pool_update_provider(context, pool['pool'])
        p = super(LoadBalancerPlugin, self).create_pool(context, pool)
        pool_id = p['id']
        try:
            driver = self._get_driver_for_provider(provider_name)
            self._pool_driver[pool_id] = driver
            driver.create_pool(context, p)
        except Exception as ex:
            try:
                self._api.loadbalancer_pool_delete(pool_id)
            except NoIdError:
                pass
            raise ex
        return p

    def update_pool(self, context, id, pool):
        old_pool = self.get_pool(context, id)
        p = super(LoadBalancerPlugin, self).update_pool(context, id, pool)
        driver = self._get_driver_for_pool(id)
        try:
            driver.update_pool(context, old_pool, p)
        except Exception as ex:
            LOG.error(ex)
        return p

    def delete_pool(self, context, id):
        p = self.get_pool(context, id)
        driver = self._get_driver_for_pool(id)
        try:
            driver.delete_pool(context, p)
        except Exception as ex:
            LOG.error(ex)
        if id in self._pool_driver:
            del self._pool_driver[id]
        super(LoadBalancerPlugin, self).delete_pool(context, id)

    def create_vip(self, context, vip):
        """ Create virtual-ip.
        """
        v = super(LoadBalancerPlugin, self).create_vip(context, vip)
        driver = self._get_driver_for_pool(v['pool_id'])
        try:
            driver.create_vip(context, v)
        except Exception as ex:
            try:
                self._api.virtual_ip_delete(v['id'])
            except NoIdError:
                pass
            raise ex
        return v

    def update_vip(self, context, id, vip):
        old_vip = self.get_vip(context, id)
        v = super(LoadBalancerPlugin, self).update_vip(context, id, vip)
        driver = self._get_driver_for_pool(v['pool_id'])
        try:
            driver.update_vip(context, old_vip, v)
        except Exception as ex:
            LOG.error(ex)
        return v

    def delete_vip(self, context, id):
        v = self.get_vip(context, id)
        driver = self._get_driver_for_pool(v['pool_id'])
        try:
            driver.delete_vip(context, v)
        except Exception as ex:
            LOG.error(ex)
        super(LoadBalancerPlugin, self).delete_vip(context, id)

    def create_member(self, context, member):
        m = super(LoadBalancerPlugin, self).create_member(context, member)
        driver = self._get_driver_for_pool(m['pool_id'])
        try:
            driver.create_member(context, m)
        except Exception as ex:
            self._api.loadbalancer_member_delete(m['id'])
            raise ex
        return m

    def update_member(self, context, id, member):
        old_member = self.get_member(context, id)
        m = super(LoadBalancerPlugin, self).update_member(context, id, member)
        driver = self._get_driver_for_pool(m['pool_id'])
        try:
            driver.update_member(context, old_member, m)
        except Exception as ex:
            LOG.error(ex)
        return m

    def delete_member(self, context, id):
        m = self.get_member(context, id)
        driver = self._get_driver_for_pool(m['pool_id'])
        try:
            driver.delete_member(context, m)
        except Exception as ex:
            LOG.error(ex)
        super(LoadBalancerPlugin, self).delete_member(context, id)
