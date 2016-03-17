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

notice('MODULAR: contrail/common-repo.pp')

case $operatingsystem
{
    CentOS: {
      yumrepo {'mos': priority => 1, exclude => 'python-thrift,nodejs'} # Contrail requires newer python-thrift and nodejs from it's repo
      package {'yum-plugin-priorities': ensure => present }
    }
    Ubuntu: {
      file { '/etc/apt/sources.list.d/contrail-3.0.0.list':
        ensure => present,
        content => 'deb http://10.20.0.2:8080/plugins/contrail-3.0/repositories/ubuntu/ / # This file is managed by Puppet. DO NOT EDIT.'
      } ->
      exec { "apt-get update":
         command => "/usr/bin/apt-get update",
      }
      file { '/etc/apt/preferences.d/contrail-3.0.1.pref':
        ensure => absent,
      }
    }
    default: {}
}


