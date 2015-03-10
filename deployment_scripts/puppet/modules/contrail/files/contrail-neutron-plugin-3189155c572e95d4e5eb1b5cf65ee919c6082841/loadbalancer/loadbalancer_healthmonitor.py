#
# Copyright (c) 2014 Juniper Networks, Inc. All rights reserved.
#

import uuid

from neutron.extensions import loadbalancer
from neutron.openstack.common import uuidutils
from vnc_api.vnc_api import IdPermsType, NoIdError
from vnc_api.vnc_api import LoadbalancerHealthmonitor
from vnc_api.vnc_api import LoadbalancerHealthmonitorType

from resource_manager import ResourceManager


class LoadbalancerHealthmonitorManager(ResourceManager):
    _loadbalancer_health_type_mapping = {
        'admin_state': 'admin_state_up',
        'monitor_type': 'type',
        'delay': 'delay',
        'timeout': 'timeout',
        'max_retries': 'max_retries',
        'http_method': 'http_method',
        'url_path': 'url_path',
        'expected_codes': 'expected_codes'
    }

    @property
    def property_type_mapping(self):
        return self._loadbalancer_health_type_mapping

    def make_properties(self, health_monitor):
        props = LoadbalancerHealthmonitorType()
        for key, mapping in self._loadbalancer_health_type_mapping.iteritems():
            if mapping in health_monitor:
                setattr(props, key, health_monitor[mapping])
        return props

    def make_dict(self, health_monitor, fields=None):
        res = {'id': health_monitor.uuid,
               'tenant_id': health_monitor.parent_uuid.replace('-', ''),
               'status': self._get_object_status(health_monitor)}

        props = health_monitor.get_loadbalancer_healthmonitor_properties()
        for key, mapping in self._loadbalancer_health_type_mapping.iteritems():
            value = getattr(props, key)
            if value is not None:
                res[mapping] = value

        pool_ids = []
        pool_back_refs = health_monitor.get_loadbalancer_pool_back_refs()
        for pool_back_ref in pool_back_refs or []:
            pool_id = {}
            pool_id['pool_id'] = pool_back_ref['uuid']
            pool_ids.append(pool_id)
        res['pools'] = pool_ids

        return self._fields(res, fields)

    def resource_read(self, id):
        return self._api.loadbalancer_healthmonitor_read(id=id)

    def resource_list(self, tenant_id=None):
        if tenant_id:
            parent_id = str(uuid.UUID(tenant_id))
        else:
            parent_id = None
        return self._api.loadbalancer_healthmonitors_list(parent_id=parent_id)

    def resource_update(self, obj):
        return self._api.loadbalancer_healthmonitor_update(obj)

    def resource_delete(self, id):
        return self._api.loadbalancer_healthmonitor_delete(id=id)

    def get_exception_notfound(self, id=None):
        return loadbalancer.HealthMonitorNotFound(monitor_id=id)

    def get_exception_inuse(self, id=None):
        return loadbalancer.HealthMonitorInUse(monitor_id=id)

    @property
    def neutron_name(self):
        return "health_monitor"

    @property
    def resource_name_plural(self):
        return "loadbalancer-healthmonitors"

    def create(self, context, health_monitor):
        """
        Create a loadbalancer_healtmonitor object.
        """
        m = health_monitor['health_monitor']
        tenant_id = self._get_tenant_id_for_create(context, m)
        project = self._project_read(project_id=tenant_id)

        uuid = uuidutils.generate_uuid()
        props = self.make_properties(m)
        id_perms = IdPermsType(enable=True)
        monitor_db = LoadbalancerHealthmonitor(
            uuid, project, loadbalancer_healthmonitor_properties=props,
            id_perms=id_perms)
        monitor_db.uuid = uuid

        self._api.loadbalancer_healthmonitor_create(monitor_db)
        return self.make_dict(monitor_db)

    def update_properties(self, monitor_db, id, m):
        props = monitor_db.get_loadbalancer_healthmonitor_properties()
        if self.update_properties_subr(props, m):
            monitor_db.set_loadbalancer_healthmonitor_properties(props)
            return True
        return False
