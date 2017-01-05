#    Copyright 2016 AT&T Corp
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
class contrail::rbac_create_domain {

  $public_vip    = $contrail::mos_public_vip
  $api_port      = $contrail::api_server_port
  $rbacutil_path = '/opt/contrail/utils'
  $confirmation  = '/bin/echo y'
  $operation     = 'create'
  $domain        = 'default-domain'
  $access_list   = 'default-api-access-list'
  $rbac_access   = hiera_hash('rbac_access', {})
  $usr           = pick($rbac_access['user'], 'admin')
  $pwd           = pick($rbac_access['password'], 'admin')
  $tenant_name   = pick($rbac_access['tenant'], 'admin')

  exec { "create default api access list":
    command => "${confirmation} | /usr/bin/sudo /usr/bin/python ${rbacutil_path}/rbacutil.py --name '${domain}:${access_list}' --op ${operation}  --os-username ${usr} --os-password ${pwd} --os-tenant-name ${tenant_name} --server ${public_ip}:${api_port}",
    unless  => "/usr/bin/sudo /usr/bin/python ${rbacutil_path}/rbacutil.py --name '${domain}:${access_list}' --op read --os-username ${usr} --os-password ${pwd} --os-tenant-name '${tenant_name}' --server ${public_vip}:${api_port}",
  }

}
