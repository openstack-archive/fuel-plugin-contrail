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
    owner   => 'contrail',
    group   => 'contrail',
    require => Package['contrail-openstack-control'],
  }

  Exec {
    provider => 'shell',
    path     => '/usr/bin:/bin:/sbin',
  }

  tweaks::ubuntu_service_override { 'supervisor-control':
    package_name => 'contrail-control',
  }

# Packages
  package { 'contrail-dns': }
  package { 'contrail-control': }
  package { 'contrail-openstack-control': }

# Contrail control config files
  file { '/etc/contrail/vnc_api_lib.ini':
    content => template('contrail/vnc_api_lib.ini.erb')
  }

  file { '/etc/contrail/contrail-control.conf':
    content => template('contrail/contrail-control.conf.erb'),
  }

  file { '/etc/contrail/contrail-dns.conf':
    content => template('contrail/contrail-dns.conf.erb'),
    require => Package['contrail-dns'],
  }

  file { '/etc/contrail/dns/contrail-named.conf':
    content => template('contrail/contrail-named.conf.erb'),
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
  service { 'contrail-named':
    ensure    => running,
    subscribe => [Package['contrail-dns'],
                  File['/etc/contrail/dns/contrail-named.conf'],
                  File['/etc/contrail/dns/contrail-rndc.conf'],
                  ]
  }
  service { 'supervisor-control':
    ensure    => $contrail::service_ensure,
    enable    => true,
    subscribe =>  [Package['contrail-openstack-control'],Package['contrail-control'],
                  File['/etc/contrail/contrail-control.conf'],
                  File['/etc/contrail/contrail-dns.conf'],
                  ],
  }

}
