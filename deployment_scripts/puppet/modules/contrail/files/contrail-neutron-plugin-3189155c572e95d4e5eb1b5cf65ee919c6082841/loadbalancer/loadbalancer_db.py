#
# Copyright (c) 2014 Juniper Networks, Inc. All rights reserved.
#

import requests
import time
import uuid

from oslo.config import cfg
from neutron.extensions import loadbalancer
from neutron.extensions.loadbalancer import LoadBalancerPluginBase
from vnc_api.vnc_api import VncApi

import loadbalancer_healthmonitor
import loadbalancer_member
import loadbalancer_pool
import virtual_ip


class LoadBalancerPluginDb(LoadBalancerPluginBase):

    def __init__(self):
        admin_user = cfg.CONF.keystone_authtoken.admin_user
        admin_password = cfg.CONF.keystone_authtoken.admin_password
        admin_tenant_name = cfg.CONF.keystone_authtoken.admin_tenant_name
        api_srvr_ip = cfg.CONF.APISERVER.api_server_ip
        api_srvr_port = cfg.CONF.APISERVER.api_server_port
        try:
            auth_host = cfg.CONF.keystone_authtoken.auth_host
        except cfg.NoSuchOptError:
            auth_host = "127.0.0.1"

        try:
            auth_protocol = cfg.CONF.keystone_authtoken.auth_protocol
        except cfg.NoSuchOptError:
            auth_protocol = "http"

        try:
            auth_port = cfg.CONF.keystone_authtoken.auth_port
        except cfg.NoSuchOptError:
            auth_port = "35357"

        try:
            auth_url = cfg.CONF.keystone_authtoken.auth_url
        except cfg.NoSuchOptError:
            auth_url = "/v2.0/tokens"

        try:
            auth_type = cfg.CONF.keystone_authtoken.auth_type
        except cfg.NoSuchOptError:
            auth_type = "keystone"

        try:
            api_server_url = cfg.CONF.APISERVER.api_server_url
        except cfg.NoSuchOptError:
            api_server_url = "/"

        # Retry till a api-server is up
        connected = False
        while not connected:
            try:
                self._api = VncApi(
                     admin_user, admin_password, admin_tenant_name,
                     api_srvr_ip, api_srvr_port, api_server_url,
                     auth_host=auth_host, auth_port=auth_port,
                     auth_protocol=auth_protocol, auth_url=auth_url,
                     auth_type=auth_type)
                connected = True
            except requests.exceptions.RequestException as e:
                time.sleep(3)

        self._pool_manager = \
            loadbalancer_pool.LoadbalancerPoolManager(self._api)
        self._vip_manager = virtual_ip.VirtualIpManager(self._api)
        self._member_manager = \
            loadbalancer_member.LoadbalancerMemberManager(self._api)
        self._monitor_manager = \
            loadbalancer_healthmonitor.LoadbalancerHealthmonitorManager(
                self._api)

    def get_api_client(self):
        return self._api

    def get_vips(self, context, filters=None, fields=None):
        return self._vip_manager.get_collection(context, filters, fields)

    def get_vip(self, context, id, fields=None):
        return self._vip_manager.get_resource(context, id, fields)

    def create_vip(self, context, vip):
        return self._vip_manager.create(context, vip)

    def update_vip(self, context, id, vip):
        return self._vip_manager.update(context, id, vip)

    def delete_vip(self, context, id):
        return self._vip_manager.delete(context, id)

    def get_pools(self, context, filters=None, fields=None):
        return self._pool_manager.get_collection(context, filters, fields)

    def get_pool(self, context, id, fields=None):
        return self._pool_manager.get_resource(context, id, fields)

    def create_pool(self, context, pool):
        return self._pool_manager.create(context, pool)

    def update_pool(self, context, id, pool):
        return self._pool_manager.update(context, id, pool)

    def delete_pool(self, context, id):
        return self._pool_manager.delete(context, id)

    def stats(self, context, pool_id):
        pass

    def create_pool_health_monitor(self, context, health_monitor, pool_id):
        """ Associate an health monitor with a pool.
        """
        m = health_monitor['health_monitor']
        try:
            pool = self._api.loadbalancer_pool_read(id=pool_id)
        except NoIdError:
            raise loadbalancer.PoolNotFound(pool_id=pool_id)

        try:
            monitor = self._api.loadbalancer_healthmonitor_read(id=m['id'])
        except NoIdError:
            raise loadbalancer.HealthMonitorNotFound(monitor_id=m['id'])

        if not context.is_admin:
            tenant_id = str(uuid.UUID(context.tenant_id))
            if tenant_id != pool.parent_uuid or \
                    tenant_id != monitor.parent_uuid:
                raise n_exc.NotAuthorized()

        pool_refs = monitor.get_loadbalancer_pool_back_refs()
        if pool_refs is not None:
            for ref in pool_refs:
                if ref['uuid'] == pool_id:
                    raise loadbalancer.PoolMonitorAssociationExists(
                        monitor_id=m['id'], pool_id=pool_id)

        pool.add_loadbalancer_healthmonitor(monitor)
        self._api.loadbalancer_pool_update(pool)

        res = {
            'id': monitor.uuid,
            'tenant_id': monitor.parent_uuid.replace('-', '')
        }
        return res

    def get_pool_health_monitor(self, context, id, pool_id, fields=None):
        """ Query a specific pool, health_monitor association.
        """
        try:
            pool = self._api.loadbalancer_pool_read(id=pool_id)
        except NoIdError:
            raise loadbalancer.PoolNotFound(pool_id=id)
        tenant_id = str(uuid.UUID(context.tenant_id))
        if not context.is_admin and tenant_id != pool.parent_uuid:
            raise loadbalancer.PoolNotFound(pool_id=id)

        in_list = False
        for mref in pool.get_loadbalancer_healthmonitor_refs() or []:
            if mref['uuid'] == id:
                in_list = True
                break

        if not in_list:
            raise loadbalancer.PoolMonitorAssociationNotFound(
                monitor_id=id, pool_id=pool_id)

        res = {
            'pool_id': pool_id,
            'monitor_id': id,
            'status': self._pool_manager._get_object_status(pool),
            'tenant_id': pool.parent_uuid.replace('-', '')
        }
        return self._pool_manager._fields(res, fields)

    def delete_pool_health_monitor(self, context, id, pool_id):
        try:
            pool = self._api.loadbalancer_pool_read(id=pool_id)
        except NoIdError:
            raise loadbalancer.PoolNotFound(pool_id=id)
        tenant_id = str(uuid.UUID(context.tenant_id))
        if not context.is_admin and tenant_id != pool.parent_uuid:
            raise loadbalancer.PoolNotFound(pool_id=id)

        try:
            monitor = self._api.loadbalancer_healthmonitor_read(id=id)
        except NoIdError:
            raise loadbalancer.HealthMonitorNotFound(monitor_id=id)

        in_list = False
        for mref in pool.get_loadbalancer_healthmonitor_refs():
            if mref['uuid'] == id:
                in_list = True
                break

        if not in_list:
            raise loadbalancer.PoolMonitorAssociationNotFound(
                monitor_id=id, pool_id=pool_id)

        pool.del_loadbalancer_healthmonitor(monitor)
        self._api.loadbalancer_pool_update(pool)

    def get_members(self, context, filters=None, fields=None):
        return self._member_manager.get_collection(context, filters, fields)

    def get_member(self, context, id, fields=None):
        return self._member_manager.get_resource(context, id, fields)

    def create_member(self, context, member):
        return self._member_manager.create(context, member)

    def update_member(self, context, id, member):
        return self._member_manager.update(context, id, member)

    def delete_member(self, context, id):
        return self._member_manager.delete(context, id)

    def get_health_monitors(self, context, filters=None, fields=None):
        return self._monitor_manager.get_collection(context, filters, fields)

    def get_health_monitor(self, context, id, fields=None):
        return self._monitor_manager.get_resource(context, id, fields)

    def create_health_monitor(self, context, health_monitor):
        return self._monitor_manager.create(context, health_monitor)

    def update_health_monitor(self, context, id, health_monitor):
        return self._monitor_manager.update(context, id, health_monitor)

    def delete_health_monitor(self, context, id):
        return self._monitor_manager.delete(context, id)
