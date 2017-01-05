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

class contrail::rbac inherits contrail::rbac_settings{

  $rbac_rules        = hiera_hash('RBAC',{})
  $rbac_wrapper_path = $contrail::rbac_settings::rbac_wrapper_path
  $public_vip    = $contrail::mos_public_vip

  notify { $rbac_wrapper_path: }

  file { "${rbac_wrapper_path}/rbac_settings.yaml":
    ensure  => present,
    content => template('contrail/rbac_settings_dump.yaml.erb'),
  }

  exec { "execute rbac custom python script":
    require => File ["${rbac_wrapper_path}/rbac_settings.yaml"],
    command => "/usr/bin/sudo /usr/bin/python ${rbac_wrapper_path}/rbac_wrapper.py ${public_ip}",
    timeout => 900,
  }

}
