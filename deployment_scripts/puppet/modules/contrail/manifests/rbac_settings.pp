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

class contrail::rbac_settings {

  $rbac_wrapper_path = '/var/lib/fuel/rbac_wrapper'
  $hiera_data_dir    = '/etc/hiera'
  $rbac_ip_port      = '127.0.0.1:9100'
  $rbac_access       = hiera_hash('access', {})
  $user_name         = pick($rbac_access['user'], 'admin')
  $user_password     = pick($rbac_access['password'], 'admin')
  $tenant_name       = pick($rbac_access['tenant'], 'admin')

  file { $rbac_wrapper_path:
    ensure => directory,
  }

  file { "${hiera_data_dir}/plugins/rbac_settings.yaml":
    ensure  => present,
    content => template('contrail/rbac_settings.yaml.erb'),
  }

  file { "${rbac_wrapper_path}/rbac_wrapper.py":
    ensure  => present,
    content => template('contrail/rbac_wrapper.py.erb'),
    require => File[$rbac_wrapper_path]
  }

  file { "${rbac_wrapper_path}/rbac_cmd.sh":
    ensure  => present,
    content => template('contrail/rbac_cmd.sh.erb'),
    require => File[$rbac_wrapper_path],
  }

}
