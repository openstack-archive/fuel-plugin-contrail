# vim: tabstop=4 shiftwidth=4 softtabstop=4

import ConfigParser
from pprint import pformat

from neutron.openstack.common import log as logging

from oslo.config import cfg
from httplib2 import Http
import re
import string
import sys
import cgitb
import uuid
import requests

from cfgm_common import exceptions as vnc_exc
from vnc_api import vnc_api

LOG = logging.getLogger(__name__)

vnc_conn = None

class QuotaDriver(object):
    """Configuration driver.

    Driver to perform necessary checks to enforce quotas and obtain
    quota information. The default driver utilizes the default values
    in neutron.conf.
    """
    quota_neutron_to_contrail_type = {
            'subnet': 'subnet',
            'network': 'virtual_network',
            'floatingip': 'floating_ip',
            'route_table': 'logical_router',
            'security_group': 'security_group',
            'security_group_rule': 'security_group_rule',
            'router': 'logical_router',
            'port': 'virtual_machine_interface',
            'pool': 'loadbalancer_pool',
            'vip': 'virtual_ip',
            };

    @classmethod
    def _get_vnc_conn(cls):
        global vnc_conn
        if vnc_conn:
            return vnc_conn
        # Retry till a api-server is up
        while True:
            try:
                vnc_conn = vnc_api.VncApi(
                    cfg.CONF.keystone_authtoken.admin_user,
                    cfg.CONF.keystone_authtoken.admin_password,
                    cfg.CONF.keystone_authtoken.admin_tenant_name,
                    cfg.CONF.APISERVER.api_server_ip,
                    cfg.CONF.APISERVER.api_server_port,
                    auth_host=cfg.CONF.keystone_authtoken.auth_host,
                    auth_port=cfg.CONF.keystone_authtoken.auth_port,
                    auth_protocol=cfg.CONF.keystone_authtoken.auth_protocol)
                return vnc_conn
            except requests.exceptions.RequestException as e:
                time.sleep(3)
    # end _get_vnc_conn

    def limit_check(self, context, tenant_id,
                    resources, values):
        """Check simple quota limits.

        For limits--those quotas for which there is no usage
        synchronization function--this method checks that a set of
        proposed values are permitted by the limit restriction.

        This method will raise a QuotaResourceUnknown exception if a
        given resource is unknown or if it is not a simple limit
        resource.

        If any of the proposed values is over the defined quota, an
        OverQuota exception will be raised with the sorted list of the
        resources which are too high.  Otherwise, the method returns
        nothing.

        :param context: The request context, for access checks.
        :param tennant_id: The tenant_id to check quota.
        :param resources: A dictionary of the registered resources.
        :param values: A dictionary of the values to check against the
                       quota.
        """

    @classmethod
    def get_tenant_quotas(cls, context, resources, tenant_id):
        try:
            default_project = cls._get_vnc_conn().project_read(
                fq_name=['default-domain', 'default-project'])
            default_quota = default_project.get_quota()
        except vnc_exc.NoIdError:
            default_quota = None
        return cls._get_tenant_quotas(context, resources, tenant_id,
                                      default_quota)

    @classmethod
    def _get_tenant_quotas(cls, context, resources, tenant_id, default_quota):
        try:
            proj_id = str(uuid.UUID(tenant_id))
            proj_obj = cls._get_vnc_conn().project_read(id=proj_id)
            quota = proj_obj.get_quota()
        except vnc_exc.NoIdError:
            return {}
        except Exception as e:
            cgitb.Hook(format="text").handle(sys.exc_info())
            raise e

        qn2c = cls.quota_neutron_to_contrail_type
        quotas = {}
        for resource in resources:
            quota_res = None
            if quota and resource in qn2c:
                quota_res = getattr(quota, qn2c[resource], None)
            if quota_res is None and default_quota and resource in qn2c:
                quota_res = getattr(default_quota, qn2c[resource], None)
                if quota_res is None:
                    quota_res = default_quota.get_defaults()
            if quota_res is None:
                quota_res = resources[resource].default
            quotas[resource] = quota_res
        return quotas

    @classmethod
    def get_all_quotas(cls, context, resources):
        try:
            default_project = cls._get_vnc_conn().project_read(
                fq_name=['default-domain', 'default-project'])
            default_quota = default_project.get_quota()
        except vnc_exc.NoIdError:
            default_quota = None

        project_list = cls._get_vnc_conn().projects_list()['projects']
        ret_list = []
        for project in project_list:
            if default_quota and (project['uuid'] == default_project.uuid):
                continue
            quotas = cls._get_tenant_quotas(context, resources, project['uuid'],
                                            default_quota)
            quotas['tenant_id'] = project['uuid']
            ret_list.append(quotas)
        return ret_list

    @classmethod
    def delete_tenant_quota(cls, context, tenant_id):
        try:
            proj_id = str(uuid.UUID(tenant_id))
            proj_obj = cls._get_vnc_conn().project_read(id=proj_id)
            quota = proj_obj.get_quota()
        except vnc_exc.NoIdError:
            return
        except Exception as e:
            cgitb.Hook(format="text").handle(sys.exc_info())
            raise e

        for k,v in quota.__dict__.items():
            if k != 'defaults':
                quota.__dict__[k] = None
        proj_obj.set_quota(quota)
        cls._get_vnc_conn().project_update(proj_obj)

    @classmethod
    def update_quota_limit(cls, context, tenant_id, resource, limit):
        try:
            proj_id = str(uuid.UUID(tenant_id))
            proj_obj = cls._get_vnc_conn().project_read(id=proj_id)
            quota = proj_obj.get_quota() or vnc_api.QuotaType()
        except vnc_exc.NoIdError:
            return
        except Exception as e:
            cgitb.Hook(format="text").handle(sys.exc_info())
            raise e

        qn2c = cls.quota_neutron_to_contrail_type
        if resource in qn2c:
            quota_method = 'set_' + qn2c[resource]
            set_quota = getattr(quota, quota_method)
            set_quota(limit)
            proj_obj.set_quota(quota)
            cls._get_vnc_conn().project_update(proj_obj)
