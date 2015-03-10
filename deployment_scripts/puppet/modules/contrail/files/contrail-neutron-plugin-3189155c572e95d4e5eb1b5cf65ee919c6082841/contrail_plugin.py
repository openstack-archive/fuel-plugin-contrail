# Copyright 2014 Juniper Networks.  All rights reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
#
# @author: Hampapur Ajay, Praneet Bachheti, Rudra Rugge, Atul Moghe

from oslo.config import cfg
import requests

from neutron.api.v2 import attributes as attr
from neutron.common import exceptions as exc
from neutron.db import portbindings_base
from neutron.db import quota_db  # noqa
from neutron.extensions import allowedaddresspairs
from neutron.extensions import external_net
from neutron.extensions import l3
from neutron.extensions import portbindings
from neutron.extensions import securitygroup
from neutron import neutron_plugin_base_v2
from neutron.openstack.common import importutils
from neutron.openstack.common import jsonutils as json
from neutron.openstack.common import log as logging
from simplejson import JSONDecodeError

LOG = logging.getLogger(__name__)

vnc_opts = [
    cfg.StrOpt('api_server_ip', default='127.0.0.1',
               help='IP address to connect to VNC controller'),
    cfg.StrOpt('api_server_port', default='8082',
               help='Port to connect to VNC controller'),
    cfg.DictOpt('contrail_extensions', default={},
                help='Enable Contrail extensions(policy, ipam)'),
]

class InvalidContrailExtensionError(exc.ServiceUnavailable):
    message = _("Invalid Contrail Extension: %(ext_name) %(ext_class)")

class NeutronPluginContrailCoreV2(neutron_plugin_base_v2.NeutronPluginBaseV2,
                                  securitygroup.SecurityGroupPluginBase,
                                  portbindings_base.PortBindingBaseMixin,
                                  external_net.External_net):

    supported_extension_aliases = ["security-group", "router",
                                   "port-security", "binding", "agent",
                                   "quotas", "external-net", "contrail",
                                   "allowed-address-pairs", "extra_dhcp_opt"]
    PLUGIN_URL_PREFIX = '/neutron'
    __native_bulk_support = False

    # patch VIF_TYPES
    portbindings.__dict__['VIF_TYPE_VROUTER'] = 'vrouter'
    portbindings.VIF_TYPES.append(portbindings.VIF_TYPE_VROUTER)

    def _parse_class_args(self):
        """Parse the contrailplugin.ini file.

        Opencontrail supports extension such as ipam, policy, these extensions
        can be configured in the plugin configuration file as shown below.
        Plugin then loads the specified extensions.
        contrail_extensions=ipam:<classpath>,policy:<classpath>
        """

        contrail_extensions = cfg.CONF.APISERVER.contrail_extensions
        # If multiple class specified for same extension, last one will win
        # according to DictOpt behavior
        for ext_name, ext_class in contrail_extensions.items():
            try:
                if not ext_class:
                    LOG.error(_('Malformed contrail extension...'))
                    continue
                self.supported_extension_aliases.append(ext_name)
                if ext_class == 'None':
                    continue
                ext_class = importutils.import_class(ext_class)
                ext_instance = ext_class()
                ext_instance.set_core(self)
                for method in dir(ext_instance):
                    for prefix in ['get', 'update', 'delete', 'create']:
                        if method.startswith('%s_' % prefix):
                            setattr(self, method,
                                    ext_instance.__getattribute__(method))
            except Exception:
                LOG.exception(_("Contrail Backend Error"))
                # Converting contrail backend error to Neutron Exception
                raise InvalidContrailExtensionError(
                    ext_name=ext_name, ext_class=ext_class)

        #keystone
        self._authn_token = None
        if cfg.CONF.auth_strategy == 'keystone':
            kcfg = cfg.CONF.keystone_authtoken
            body = '{"auth":{"passwordCredentials":{'
            body += ' "username": "%s",' % (kcfg.admin_user)
            body += ' "password": "%s"},' % (kcfg.admin_password)
            body += ' "tenantName":"%s"}}' % (kcfg.admin_tenant_name)

            self._authn_body = body
            self._authn_token = cfg.CONF.keystone_authtoken.admin_token
            self._keystone_url = "%s://%s:%s%s" % (
                cfg.CONF.keystone_authtoken.auth_protocol,
                cfg.CONF.keystone_authtoken.auth_host,
                cfg.CONF.keystone_authtoken.auth_port,
                "/v2.0/tokens")

    def __init__(self):
        super(NeutronPluginContrailCoreV2, self).__init__()
        portbindings_base.register_port_dict_function()
        cfg.CONF.register_opts(vnc_opts, 'APISERVER')
        self._parse_class_args()
        self.base_binding_dict = self._get_base_binding_dict()

    def _get_base_binding_dict(self):
        binding = {
            portbindings.VIF_TYPE: portbindings.VIF_TYPE_VROUTER,
        }
        # In havana portbindings.VIF_DETAILS is not defined by neutron
        try:
            binding[portbindings.VIF_DETAILS] = {
                # TODO(praneetb): Replace with new VIF security details
                portbindings.CAP_PORT_FILTER:
                'security-group' in self.supported_extension_aliases
            }
        except AttributeError:
            pass
        return binding

    def get_agents(self, context, filters=None, fields=None):
        # This method is implemented so that horizon is happy
        return []

    def _request_api_server(self, url, data=None, headers=None):
        # Attempt to post to Api-Server
        response = requests.post(url, data=data, headers=headers)
        if (response.status_code == requests.codes.unauthorized):
            # Get token from keystone and save it for next request
            response = requests.post(self._keystone_url,
                data=self._authn_body,
                headers={'Content-type': 'application/json'})
            if (response.status_code == requests.codes.ok):
                # plan is to re-issue original request with new token
                auth_headers = headers or {}
                authn_content = json.loads(response.text)
                self._authn_token = authn_content['access']['token']['id']
                auth_headers['X-AUTH-TOKEN'] = self._authn_token
                response = self._request_api_server(url, data, auth_headers)
            else:
                raise RuntimeError('Authentication Failure')
        return response

    def _request_api_server_authn(self, url, data=None, headers=None):
        authn_headers = headers or {}
        if self._authn_token is not None:
            authn_headers['X-AUTH-TOKEN'] = self._authn_token
        response = self._request_api_server(url, data, headers=authn_headers)
        return response

    def _relay_request(self, url_path, data=None):
        """Send received request to api server."""

        url = "http://%s:%s%s" % (cfg.CONF.APISERVER.api_server_ip,
                                  cfg.CONF.APISERVER.api_server_port,
                                  url_path)

        return self._request_api_server_authn(
            url, data=data, headers={'Content-type': 'application/json'})

    def _request_backend(self, context, data_dict, obj_name, action):
        context_dict = self._encode_context(context, action, obj_name)
        data = json.dumps({'context': context_dict, 'data': data_dict})

        url_path = "%s/%s" % (self.PLUGIN_URL_PREFIX, obj_name)
        response = self._relay_request(url_path, data=data)
        try:
            return response.status_code, response.json()
        except JSONDecodeError:
            return response.status_code, {'message': response.content}

    def _encode_context(self, context, operation, apitype):
        cdict = {'user_id': getattr(context, 'user_id', ''),
                 'is_admin': getattr(context, 'is_admin', False),
                 'operation': operation,
                 'type': apitype,
                 'tenant_id': getattr(context, 'tenant_id', None)}
        if context.roles:
            cdict['roles'] = context.roles
        if context.tenant:
            cdict['tenant'] = context.tenant
        return cdict

    def _encode_resource(self, resource_id=None, resource=None, fields=None,
                         filters=None):
        resource_dict = {}
        if resource_id:
            resource_dict['id'] = resource_id
        if resource:
            resource_dict['resource'] = resource
        resource_dict['filters'] = filters
        resource_dict['fields'] = fields
        return resource_dict

    def _prune(self, resource_dict, fields):
        if fields:
            return dict(((key, item) for key, item in resource_dict.items()
                         if key in fields))
        return resource_dict

    def _transform_response(self, status_code, info=None, obj_name=None,
                            fields=None):
        if status_code == requests.codes.ok:
            if not isinstance(info, list):
                return self._prune(info, fields)
            else:
                return [self._prune(items, fields) for items in info]
        self._raise_contrail_error(info, obj_name)

    def _raise_contrail_error(self, info, obj_name):
        exc_name = info.get('exception')
        if exc_name:
            if exc_name == 'BadRequest' and 'resource' not in info:
                info['resource'] = obj_name
            if hasattr(exc, exc_name):
                raise getattr(exc, exc_name)(**info)
            if hasattr(l3, exc_name):
                raise getattr(l3, exc_name)(**info)
            if hasattr(securitygroup, exc_name):
                raise getattr(securitygroup, exc_name)(**info)
            if hasattr(allowedaddresspairs, exc_name):
                raise getattr(allowedaddresspairs, exc_name)(**info)
        raise exc.NeutronException(**info)

    def _create_resource(self, res_type, context, res_data):
        """Create a resource in API server.

        This method encodes neutron model, and sends it to the
        contrail api server.
        """

        for key, value in res_data[res_type].items():
            if value == attr.ATTR_NOT_SPECIFIED:
                del res_data[res_type][key]

        res_dict = self._encode_resource(resource=res_data[res_type])
        status_code, res_info = self._request_backend(context, res_dict,
                                                      res_type, 'CREATE')
        res_dicts = self._transform_response(status_code, info=res_info,
                                             obj_name=res_type)
        LOG.debug("create_%(res_type)s(): %(res_dicts)s",
                  {'res_type': res_type, 'res_dicts': res_dicts})

        return res_dicts

    def _get_resource(self, res_type, context, id, fields):
        """Get a resource from API server.

        This method gets a resource from the contrail api server
        """

        res_dict = self._encode_resource(resource_id=id, fields=fields)
        status_code, res_info = self._request_backend(context, res_dict,
                                                      res_type, 'READ')
        res_dicts = self._transform_response(status_code, info=res_info,
                                             fields=fields, obj_name=res_type)
        LOG.debug("get_%(res_type)s(): %(res_dicts)s",
                  {'res_type': res_type, 'res_dicts': res_dicts})

        return res_dicts

    def _update_resource(self, res_type, context, id, res_data):
        """Update a resource in API server.

        This method updates a resource in the contrail api server
        """

        res_dict = self._encode_resource(resource_id=id,
                                         resource=res_data[res_type])
        status_code, res_info = self._request_backend(context, res_dict,
                                                      res_type, 'UPDATE')
        res_dicts = self._transform_response(status_code, info=res_info,
                                             obj_name=res_type)
        LOG.debug("update_%(res_type)s(): %(res_dicts)s",
                  {'res_type': res_type, 'res_dicts': res_dicts})

        return res_dicts

    def _delete_resource(self, res_type, context, id):
        """Delete a resource in API server

        This method deletes a resource in the contrail api server
        """

        res_dict = self._encode_resource(resource_id=id)
        LOG.debug("delete_%(res_type)s(): %(id)s",
                  {'res_type': res_type, 'id': id})
        status_code, res_info = self._request_backend(context, res_dict,
                                                      res_type, 'DELETE')
        if status_code != requests.codes.ok:
            self._raise_contrail_error(info=res_info,
                                       obj_name=res_type)

    def _list_resource(self, res_type, context, filters, fields):
        res_dict = self._encode_resource(filters=filters, fields=fields)
        status_code, res_info = self._request_backend(context, res_dict,
                                                      res_type, 'READALL')
        res_dicts = self._transform_response(status_code, info=res_info,
                                             fields=fields, obj_name=res_type)
        LOG.debug(
            "get_%(res_type)s(): filters: %(filters)r data: %(res_dicts)r",
            {'res_type': res_type, 'filters': filters,
             'res_dicts': res_dicts})

        return res_dicts

    def _count_resource(self, res_type, context, filters):
        res_dict = self._encode_resource(filters=filters)
        status_code, res_count = self._request_backend(context, res_dict,
                                                       res_type, 'READCOUNT')
        LOG.debug("get_%(res_type)s_count(): %(res_count)r",
                  {'res_type': res_type, 'res_count': res_count})
        return res_count

    def _get_network(self, context, id, fields=None):
        return self._get_resource('network', context, id, fields)

    def create_network(self, context, network):
        """Creates a new Virtual Network."""

        return self._create_resource('network', context, network)

    def get_network(self, context, network_id, fields=None):
        """Get the attributes of a particular Virtual Network."""

        return self._get_network(context, network_id, fields)

    def update_network(self, context, network_id, network):
        """Updates the attributes of a particular Virtual Network."""

        return self._update_resource('network', context, network_id,
                                     network)

    def delete_network(self, context, network_id):
        """Creates a new Virtual Network.

        Deletes the network with the specified network identifier
        belonging to the specified tenant.
        """

        self._delete_resource('network', context, network_id)

    def get_networks(self, context, filters=None, fields=None):
        """Get the list of Virtual Networks."""

        return self._list_resource('network', context, filters,
                                   fields)

    def get_networks_count(self, context, filters=None):
        """Get the count of Virtual Network."""

        networks_count = self._count_resource('network', context, filters)
        return networks_count['count']

    def create_subnet(self, context, subnet):
        """Creates a new subnet, and assigns it a symbolic name."""

        if subnet['subnet']['gateway_ip'] is None:
            subnet['subnet']['gateway_ip'] = '0.0.0.0'

        if subnet['subnet']['host_routes'] != attr.ATTR_NOT_SPECIFIED:
            if (len(subnet['subnet']['host_routes']) >
                    cfg.CONF.max_subnet_host_routes):
                raise exc.HostRoutesExhausted(subnet_id=subnet[
                    'subnet'].get('id', _('new subnet')),
                    quota=cfg.CONF.max_subnet_host_routes)

        subnet_created = self._create_resource('subnet', context, subnet)
        return self._make_subnet_dict(subnet_created)

    def _make_subnet_dict(self, subnet):
        if 'gateway_ip' in subnet and subnet['gateway_ip'] == '0.0.0.0':
            subnet['gateway_ip'] = None
        return subnet

    def _get_subnet(self, context, subnet_id, fields=None):
        subnet = self._get_resource('subnet', context, subnet_id, fields)
        return self._make_subnet_dict(subnet)

    def get_subnet(self, context, subnet_id, fields=None):
        """Get the attributes of a particular subnet."""

        return self._get_subnet(context, subnet_id, fields)

    def update_subnet(self, context, subnet_id, subnet):
        """Updates the attributes of a particular subnet."""

        subnet = self._update_resource('subnet', context, subnet_id, subnet)
        return self._make_subnet_dict(subnet)

    def delete_subnet(self, context, subnet_id):
        """
        Deletes the subnet with the specified subnet identifier
        belonging to the specified tenant.
        """

        self._delete_resource('subnet', context, subnet_id)

    def get_subnets(self, context, filters=None, fields=None):
        """Get the list of subnets."""

        return [self._make_subnet_dict(s)
                for s in self._list_resource(
                    'subnet', context, filters, fields)]

    def get_subnets_count(self, context, filters=None):
        """Get the count of subnets."""

        subnets_count = self._count_resource('subnet', context, filters)
        return subnets_count['count']

    def _extend_port_dict_security_group(self, port_res, port_db):
        # Security group bindings will be retrieved from the sqlalchemy
        # model. As they're loaded eagerly with ports because of the
        # joined load they will not cause an extra query.
        port_res[securitygroup.SECURITYGROUPS] = port_db.get(
            'security_groups', []) or []
        return port_res

    def _make_port_dict(self, port, fields=None):
        """filters attributes of a port based on fields."""

        if not fields:
            port.update(self.base_binding_dict)
        else:
            for key in self.base_binding_dict:
                if key in fields:
                    port.update(self.base_binding_dict[key])
        return port

    def _get_port(self, context, id, fields=None):
        port = self._get_resource('port', context, id, fields)
        return self._make_port_dict(port)

    def _update_ips_for_port(self, context, network_id, port_id, original_ips,
                             new_ips):
        """Add or remove IPs from the port."""

        # These ips are still on the port and haven't been removed
        prev_ips = []

        # the new_ips contain all of the fixed_ips that are to be updated
        if len(new_ips) > cfg.CONF.max_fixed_ips_per_port:
            msg = _('Exceeded maximim amount of fixed ips per port')
            raise exc.InvalidInput(error_message=msg)

        # Remove all of the intersecting elements
        for original_ip in original_ips[:]:
            for new_ip in new_ips[:]:
                if ('ip_address' in new_ip and
                        original_ip['ip_address'] == new_ip['ip_address']):
                    original_ips.remove(original_ip)
                    new_ips.remove(new_ip)
                    prev_ips.append(original_ip)

        return new_ips, prev_ips

    def create_port(self, context, port):
        """Creates a port on the specified Virtual Network."""

        port = self._create_resource('port', context, port)
        return self._make_port_dict(port)

    def get_port(self, context, port_id, fields=None):
        """Get the attributes of a particular port."""

        return self._get_port(context, port_id, fields)

    def update_port(self, context, port_id, port):
        """Updates a port.

        Updates the attributes of a port on the specified Virtual
        Network.
        """

        if 'fixed_ips' in port['port']:
            original = self._get_port(context, port_id)
            added_ips, prev_ips = self._update_ips_for_port(
                context, original['network_id'], port_id,
                original['fixed_ips'], port['port']['fixed_ips'])
            port['port']['fixed_ips'] = prev_ips + added_ips

        port = self._update_resource('port', context, port_id, port)
        return self._make_port_dict(port)

    def delete_port(self, context, port_id):
        """Deletes a port.

        Deletes a port on a specified Virtual Network,
        if the port contains a remote interface attachment,
        the remote interface is first un-plugged and then the port
        is deleted.
        """

        self._delete_resource('port', context, port_id)

    def get_ports(self, context, filters=None, fields=None):
        """Get all ports.

        Retrieves all port identifiers belonging to the
        specified Virtual Network with the specfied filter.
        """

        return [self._make_port_dict(p)
                for p in self._list_resource('port', context, filters, fields)]

    def get_ports_count(self, context, filters=None):
        """Get the count of ports."""

        ports_count = self._count_resource('port', context, filters)
        return ports_count['count']

    # Router API handlers
    def create_router(self, context, router):
        """Creates a router.

        Creates a new Logical Router, and assigns it
        a symbolic name.
        """

        return self._create_resource('router', context, router)

    def get_router(self, context, router_id, fields=None):
        """Get the attributes of a router."""

        return self._get_resource('router', context, router_id, fields)

    def update_router(self, context, router_id, router):
        """Updates the attributes of a router."""

        return self._update_resource('router', context, router_id,
                                     router)

    def delete_router(self, context, router_id):
        """Deletes a router."""

        self._delete_resource('router', context, router_id)

    def get_routers(self, context, filters=None, fields=None):
        """Retrieves all router identifiers."""

        return self._list_resource('router', context, filters, fields)

    def get_routers_count(self, context, filters=None):
        """Get the count of routers."""

        routers_count = self._count_resource('router', context, filters)
        return routers_count['count']

    def add_router_interface(self, context, router_id, interface_info):
        """Add interface to a router."""

        if not interface_info:
            msg = _("Either subnet_id or port_id must be specified")
            raise exc.BadRequest(resource='router', msg=msg)

        if 'port_id' in interface_info:
            if 'subnet_id' in interface_info:
                msg = _("Cannot specify both subnet-id and port-id")
                raise exc.BadRequest(resource='router', msg=msg)

        res_dict = self._encode_resource(resource_id=router_id,
                                         resource=interface_info)
        status_code, res_info = self._request_backend(context, res_dict,
                                                      'router', 'ADDINTERFACE')
        if status_code != requests.codes.ok:
            self._raise_contrail_error(info=res_info,
                                       obj_name='add_router_interface')
        return res_info

    def remove_router_interface(self, context, router_id, interface_info):
        """Delete interface from a router."""

        if not interface_info:
            msg = _("Either subnet_id or port_id must be specified")
            raise exc.BadRequest(resource='router', msg=msg)

        res_dict = self._encode_resource(resource_id=router_id,
                                         resource=interface_info)
        status_code, res_info = self._request_backend(context, res_dict,
                                                      'router', 'DELINTERFACE')
        if status_code != requests.codes.ok:
            self._raise_contrail_error(info=res_info,
                                       obj_name='remove_router_interface')
        return res_info

    # Floating IP API handlers
    def create_floatingip(self, context, floatingip):
        """Creates a floating IP."""

        return self._create_resource('floatingip', context, floatingip)

    def update_floatingip(self, context, fip_id, floatingip):
        """Updates the attributes of a floating IP."""

        return self._update_resource('floatingip', context, fip_id,
                                     floatingip)

    def get_floatingip(self, context, fip_id, fields=None):
        """Get the attributes of a floating ip."""

        return self._get_resource('floatingip', context, fip_id, fields)

    def delete_floatingip(self, context, fip_id):
        """Deletes a floating IP."""

        self._delete_resource('floatingip', context, fip_id)

    def get_floatingips(self, context, filters=None, fields=None):
        """Retrieves all floating ips identifiers."""

        return self._list_resource('floatingip', context, filters, fields)

    def get_floatingips_count(self, context, filters=None):
        """Get the count of floating IPs."""

        fips_count = self._count_resource('floatingip', context, filters)
        return fips_count['count']

    # Security Group handlers
    def create_security_group(self, context, security_group):
        """Creates a Security Group."""

        return self._create_resource('security_group', context,
                                     security_group)

    def get_security_group(self, context, sg_id, fields=None, tenant_id=None):
        """Get the attributes of a security group."""

        return self._get_resource('security_group', context, sg_id, fields)

    def update_security_group(self, context, sg_id, security_group):
        """Updates the attributes of a security group."""

        return self._update_resource('security_group', context, sg_id,
                                     security_group)

    def delete_security_group(self, context, sg_id):
        """Deletes a security group."""

        self._delete_resource('security_group', context, sg_id)

    def get_security_groups(self, context, filters=None, fields=None,
                            sorts=None, limit=None, marker=None,
                            page_reverse=False):
        """Retrieves all security group identifiers."""

        return self._list_resource('security_group', context,
                                   filters, fields)

    def get_security_groups_count(self, context, filters=None):
        return 0

    def get_security_group_rules_count(self, context, filters=None):
        return 0

    def create_security_group_rule(self, context, security_group_rule):
        """Creates a security group rule."""

        return self._create_resource('security_group_rule', context,
                                     security_group_rule)

    def delete_security_group_rule(self, context, sg_rule_id):
        """Deletes a security group rule."""

        self._delete_resource('security_group_rule', context, sg_rule_id)

    def get_security_group_rule(self, context, sg_rule_id, fields=None):
        """Get the attributes of a security group rule."""

        return self._get_resource('security_group_rule', context,
                                  sg_rule_id, fields)

    def get_security_group_rules(self, context, filters=None, fields=None,
                                 sorts=None, limit=None, marker=None,
                                 page_reverse=False):
        """Retrieves all security group rules."""

        return self._list_resource('security_group_rule', context,
                                   filters, fields)
