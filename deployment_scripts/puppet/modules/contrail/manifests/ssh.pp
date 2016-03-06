#    Copyright 2015 Mirantis, Inc.
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

class contrail::ssh ( $password_auth = 'yes',$root_login = 'yes' ) {

  $ssh_service = $operatingsystem ? {
    'Ubuntu' => 'ssh',
    'CentOS' => 'sshd'
  }

  exec { 'Update-PasswordAuthentication':
    path    => '/bin:/usr/bin',
    command => "sed -i -e 's/^PasswordAuthentication.*/PasswordAuthentication ${password_auth}/g' /etc/ssh/sshd_config",
    notify  => Service[$ssh_service]
  }
  exec { 'Update-PermitRootLogin':
    path    => '/bin:/usr/bin',
    command => "sed -i -e 's/^PermitRootLogin.*/PermitRootLogin ${root_login}/g' /etc/ssh/sshd_config",
    notify  => Service[$ssh_service]
  }

  service { $ssh_service:
    ensure    => running,
  }
}