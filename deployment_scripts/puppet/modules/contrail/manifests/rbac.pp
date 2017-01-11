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
class contrail::rbac {

  include contrail::rbac_settings

  $rbac_wrapper_path = '/var/lib/fuel/rbac_wrapper'
  $public_vip        = $contrail::mos_public_vip
  $api_port          = $contrail::api_server_port
  $rbac_ip_port      = $contrail::rbac_settings::rbac_ip_port
  $rbacutil_path     = '/opt/contrail/utils'
  $confirmation      = '/bin/echo y'
  $domain            = 'default-domain'
  $access_list       = 'default-api-access-list'
  $user_name         = $contrail::rbac_settings::user_name
  $user_password     = $contrail::rbac_settings::user_password
  $tenant_name       = $contrail::rbac_settings::tenant_name
  $rbac_rules        = hiera_hash('rbac_rules', {})

  file { "${rbac_wrapper_path}/rbac_settings.yaml":
    ensure  => present,
    content => template('contrail/rbac_settings_dump.yaml.erb'),
    backup  => '.puppet-bak',
  }

  exec { 'create default api access list':
    command => "${confirmation} | sudo python ${rbacutil_path}/rbacutil.py --name '${domain}:${access_list}' --op create --os-username ${user_name} --os-password ${user_password} --os-tenant-name ${tenant_name} --server ${rbac_ip_port}",
    unless  => "sudo python ${rbacutil_path}/rbacutil.py --name '${domain}:${access_list}' --op read --os-username ${user_name} --os-password ${user_password} --os-tenant-name '${tenant_name}' --server ${rbac_ip_port}",
    path    => '/bin:/usr/bin:/usr/local/bin',
    require => File["${rbac_wrapper_path}/rbac_settings.yaml"],
  }

  exec { 'execute rbac custom python script':
    command     => "sudo python ${rbac_wrapper_path}/rbac_wrapper.py ${rbac_ip_port}",
    path        => '/bin:/usr/bin:/usr/local/bin',
    timeout     => 900,
    require     => Exec['create default api access list'],
    subscribe   => File["${rbac_wrapper_path}/rbac_settings.yaml"],
    refreshonly => true,
  }

  File <| require == File[$rbac_wrapper_path] |> -> File["${rbac_wrapper_path}/rbac_settings.yaml"]

}
