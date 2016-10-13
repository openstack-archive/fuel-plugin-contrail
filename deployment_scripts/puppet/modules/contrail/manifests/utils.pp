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

class contrail::utils {

  sysctl::value {
    'net.ipv4.conf.all.rp_filter':     value => '2';
    'net.ipv4.conf.default.rp_filter': value => '2';
  }

  case $::operatingsystem {
    Ubuntu: {
      apt::pin { 'contrail-pin-100':
        order    => '100',
        packages => '*',
        priority => '1200',
        label    => 'contrail',
      }
      $pkgs = [
        'contrail-nodemgr', 'contrail-setup', 'contrail-utils', 'ifenslave-2.6',
        'openjdk-7-jre-headless', 'patch', 'python-contrail', 'python-crypto',
        'python-netaddr', 'python-paramiko', 'supervisor', 'tzdata', 'python-urllib3',
      ]
      Package<| (title == 'tzdata') |> {
        require => Apt::Pin['contrail-pin-100'],
      } -> Package<| (title != 'tzdata') |>
    }
    CentOS: {
      $pkgs     = [
        'contrail-fabric-utils', 'contrail-setup', 'java-1.7.0-openjdk',
        'patch', 'python-netaddr', 'python-paramiko'
      ]
      $pip_pkgs = ['Fabric-1.7.5']
    }
    default: {}
  }

  class { 'contrail::package':
    install     => $pkgs,
    pip_install => $pip_pkgs,
  } ->

  file { '/etc/contrail/vnc_api_lib.ini':
    content => template('contrail/vnc_api_lib.ini.erb')
  }
}
