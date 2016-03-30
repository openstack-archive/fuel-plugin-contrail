#    Copyright 2016 Mirantis, Inc.
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

class contrail::ssh
(
  $password_auth     = no,
  $permit_root_login = no,
){

    $ssh_service = $::operatingsystem ? {
      'Ubuntu' => 'ssh',
      'CentOS' => 'sshd'
    }

    file_line { 'Update-PasswordAuthentication':
      ensure => present,
      path   => '/etc/ssh/sshd_config',
      line   => "PasswordAuthentication = ${password_auth}",
      match  => '.*PasswordAuthentication.*',
      notify => Service[$ssh_service],
    }

    file_line { 'Update-PermitRootLogin':
      ensure => present,
      path   => '/etc/ssh/sshd_config',
      line   => "PermitRootLogin = ${permit_root_login}",
      match  => '.*PermitRootLogin.*',
      notify => Service[$ssh_service],
    }

    service { $ssh_service:
      ensure    => running,
    }

}
