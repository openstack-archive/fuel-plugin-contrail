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

class contrail::control {

# Resources defaults
  Package { ensure => present }

  File {
    ensure  => present,
    mode    => '0644',
    owner   => root,
    group   => root,
    require => Package['contrail-openstack-control'],
  }

# Packages
  package { 'contrail-dns': }
  package { 'contrail-control': } ->
  package { 'contrail-openstack-control': }

# Contrail control config files
  file { '/etc/contrail/contrail-control.conf':
    content => template('contrail/contrail-control.conf.erb'),
  }

  file { '/etc/contrail/contrail-dns.conf':
    content => template('contrail/contrail-dns.conf.erb'),
    require => Package['contrail-dns'],
  }

  file { '/etc/contrail/dns/contrail-named.conf':
    source  => 'puppet:///modules/contrail/contrail-named.conf',
    require => Package['contrail-dns'],
  }

  file { '/etc/contrail/dns/contrail-rndc.conf':
    source  => 'puppet:///modules/contrail/contrail-rndc.conf',
    require => Package['contrail-dns'],
  }

  file { '/etc/contrail/contrail-control-nodemgr.conf':
    content => template('contrail/contrail-control-nodemgr.conf.erb'),
  }


# Control service
  service { 'supervisor-control':
    ensure      => running,
    enable      => true,
    require     => Package['contrail-openstack-control'],
    subscribe   => [File['/etc/contrail/contrail-control.conf'],
                    File['/etc/contrail/contrail-dns.conf'],
                    File['/etc/contrail/dns/contrail-named.conf'],
                    File['/etc/contrail/dns/contrail-rndc.conf'],
                    ],
  }

}