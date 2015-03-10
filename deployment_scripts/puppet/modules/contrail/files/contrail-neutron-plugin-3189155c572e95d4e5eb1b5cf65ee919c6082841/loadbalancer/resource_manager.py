#
# Copyright (c) 2014 Juniper Networks, Inc. All rights reserved.
#

from abc import ABCMeta, abstractmethod, abstractproperty
from eventlet import greenthread
from neutron.common import exceptions as n_exc
from neutron.extensions import loadbalancer
from neutron.plugins.common import constants
from vnc_api.vnc_api import NoIdError, RefsExistError
import six
import uuid

class LoadbalancerMethodInvalid(n_exc.BadRequest):
    message = _("Method %(lb_method)s not supported for pool %(pool_id)s")


@six.add_metaclass(ABCMeta)
class ResourceManager(object):
    _max_project_read_attempts = 3

    def __init__(self, api):
        self._api = api

    @abstractproperty
    def property_type_mapping(self):
        """ Mapping from property name to neutron dict key.
        """
        pass

    @abstractmethod
    def make_properties(self, resource):
        """ Returns the properties for the specified resource.
        """
        pass

    @abstractmethod
    def make_dict(self, resource, fields):
        """ Return the contrail api resource in the dictionary format
        expected by neutron.
        """
        pass

    @abstractmethod
    def resource_read(self, id):
        """ Read the specified resource from the api server.
        """
        pass

    @abstractmethod
    def resource_list(self, tenant_id):
        """ Returns the list of objects from the api server.
        """
        pass

    @abstractmethod
    def resource_update(self, obj):
        """ Call the update method.
        """
        pass

    @abstractmethod
    def resource_delete(self, id):
        """ Delete the specified resource from the api server.
        """
        pass

    @abstractproperty
    def get_exception_notfound(self, id):
        """ Returns the correct NotFound exception.
        """
        pass

    @abstractproperty
    def get_exception_inuse(self, id):
        """ Returns the correct NotFound exception.
        """
        pass

    @abstractproperty
    def neutron_name(self):
        """ Resource name in a request from neutron.
        """
        pass

    @abstractproperty
    def resource_name_plural(self):
        """ Resource list name in a list response from api server.
        """
        pass

    @abstractmethod
    def create(self, context, resource):
        """ Create resource.
        """
        pass

    @abstractmethod
    def update_properties(self, obj, id, resource):
        """ Update the resource properties
        """
        return False

    def update_object(self, obj, id, resource):
        """ Update object metadata other than properties
        """
        return False

    def _get_tenant_id_for_create(self, context, resource):
        if context.is_admin and 'tenant_id' in resource:
            tenant_id = resource['tenant_id']
        elif ('tenant_id' in resource and
              resource['tenant_id'] != context.tenant_id):
            reason = 'Cannot create resource for another tenant'
            raise n_exc.AdminRequired(reason=reason)
        else:
            tenant_id = context.tenant_id
        return tenant_id

    def _get_resource_name(self, resource, parent, name, uuid):
        """ Generate an unique name. This is display name if there are
        no conflicts or display_name + uuid.
        """
        fq_name = list(parent.fq_name)
        fq_name.append(name)
        try:
            obj = self._api.fq_name_to_id(resource, fq_name)
        except NoIdError:
            return name

        return name + '-' + uuid

    def _is_authorized(self, context, resource):
        return context.is_admin or context.tenant_id == resource['tenant_id']

    def _project_read(self, project_id):
        """ Reads the project from the api server. The project will be
        created it does not yet exist.
        """
        for i in range(self._max_project_read_attempts):
            try:
                return self._api.project_read(id=str(uuid.UUID(project_id)))
            except NoIdError:
                pass
            greenthread.sleep(1)
        raise n_exc.TenantNetworksDisabled()

    def _fields(self, resource, fields):
        if fields:
            return dict(((key, item) for key, item in resource.items()
                         if key in fields))
        return resource

    def _apply_filter(self, resource, filters):
        if filters is None:
            return True
        for key, value in filters.iteritems():
            if key in resource and not resource[key] in value:
                return False
        return True

    def _get_object_status(self, obj):
        id_perms = obj.get_id_perms()
        if id_perms and id_perms.enable:
            return constants.ACTIVE
        return constants.PENDING_DELETE

    def _get_object_description(self, obj):
        id_perms = obj.get_id_perms()
        if id_perms is None:
            return None
        return id_perms.description

    def _get_object_tenant_id(self, obj):
        proj_fq_name = obj.get_fq_name()[0:2]
        try:
            proj = self._api.project_read(fq_name=proj_fq_name)
        except NoIdError:
            return None

        return proj.uuid

    def get_resource(self, context, id, fields=None):
        """ Implement GET by uuid.
        """
        try:
            obj = self.resource_read(id=id)
        except NoIdError:
            raise self.get_exception_notfound(id=id)
        tenant_id = str(uuid.UUID(context.tenant_id))
        project_id = self._get_object_tenant_id(obj)
        if not context.is_admin and tenant_id != project_id:
            raise self.get_exception_notfound(id=id)
        return self.make_dict(obj, fields)

    def _get_resource_dict(self, uuid, filters, fields):
        try:
            obj = self.resource_read(id=uuid)
        except NoIdError:
            return None
        res = self.make_dict(obj, None)
        if not self._apply_filter(res, filters):
            return None
        return self._fields(res, fields)

    def get_collection(self, context, filters=None, fields=None):
        """ Generic implementation of list command.
        """

        response = []

        if filters and 'id' in filters:
            for v in filters['id']:
                res = self._get_resource_dict(v, filters, fields)
                if res is not None and self._is_authorized(context, res):
                    response.append(res)
            return response

        tenant_id = None
        if not context.is_admin:
            tenant_id = context.tenant_id
        obj_list = self.resource_list(tenant_id=tenant_id)

        if self.resource_name_plural not in obj_list:
            return response

        for v in obj_list[self.resource_name_plural]:
            res = self._get_resource_dict(v['uuid'], filters, fields)
            if res is not None:
                response.append(res)
        return response

    def delete(self, context, id):
        if not context.is_admin:
            try:
                obj = self.resource_read(id=id)
            except NoIdError:
                raise self.get_exception_notfound(id=id)
            tenant_id = str(uuid.UUID(context.tenant_id))
            project_id = self._get_object_tenant_id(obj)
            if tenant_id != project_id:
                raise n_exc.NotAuthorized()

        try:
            self.resource_delete(id=id)
        except NoIdError:
            raise self.get_exception_notfound(id=id)
        except RefsExistError:
            raise self.get_exception_inuse(id=id)

    def update_properties_subr(self, props, resource):
        """ Update the DB properties object from the neutron parameters.
        """
        change = False
        for key, mapping in self.property_type_mapping.iteritems():
            if mapping not in resource:
                continue
            if getattr(props, key) != resource[mapping]:
                setattr(props, key, resource[mapping])
                change = True

        return change

    def update(self, context, id, resource):
        """ Update the resource.
        """
        try:
            obj = self.resource_read(id=id)
        except NoIdError:
            raise self.get_exception_notfound(id=id)

        id_perms = obj.get_id_perms()
        if not id_perms or not id_perms.enable:
            raise loadbalancer.StateInvalid(id=id,
                                            state=constants.PENDING_DELETE)
        r = resource[self.neutron_name]
        if r:
            update = False
            if 'description' in r and id_perms.description != r['description']:
                id_perms.description = r['description']
                obj.set_id_perms(id_perms)
                update = True

            if self.update_properties(obj, id, r):
                update = True
            if self.update_object(obj, id, r):
                update = True

            if update:
                self.resource_update(obj)

        return self.make_dict(obj)
