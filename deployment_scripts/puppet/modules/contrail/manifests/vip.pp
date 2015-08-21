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
class contrail::vip {

  Package {
    ensure => installed,
  }
  File {
    ensure  => present,
    mode    => '0644',
    owner   => root,
    group   => root,
  }

# Packages
  package { 'keepalived': } ->
  package { 'haproxy': }

# Configs
  file { '/etc/keepalived/keepalived.conf':
    content => template('contrail/keepalived.conf.erb'),
  }
  file { '/etc/haproxy/haproxy.cfg':
    content => template('contrail/haproxy.cfg.erb'),
  }

# Services
  service { 'keepalived':
    ensure    => running,
    enable    => true,
    require   => Package['keepalived'],
    subscribe => File['/etc/keepalived/keepalived.conf'],
  }
  service { 'haproxy':
    ensure    => running,
    enable    => true,
    require   => Package['haproxy'],
    subscribe => File['/etc/haproxy/haproxy.cfg'],
  }

}