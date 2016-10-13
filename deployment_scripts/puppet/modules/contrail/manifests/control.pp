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

  contrail_control_config {
    'DEFAULT/hostip':    value => $contrail::address;
    'DEFAULT/hostname':  value => $::fqdn;
    'DEFAULT/log_file':  value => '/var/log/contrail/contrail-control.log';
    'DEFAULT/log_level': value => 'SYS_NOTICE';
    'DEFAULT/log_local': value => '1';
    'DISCOVERY/server':  value => $contrail::contrail_private_vip;
    'IFMAP/certs_store': value => ' ';
    'IFMAP/password':    value => $contrail::address;
    'IFMAP/user':        value => $contrail::address;
  }

  contrail_dns_config {
    'DEFAULT/hostip':    value => $contrail::address;
    'DEFAULT/hostname':  value => $::fqdn;
    'DEFAULT/log_file':  value => '/var/log/contrail/contrail-dns.log';
    'DEFAULT/log_level': value => 'SYS_NOTICE';
    'DEFAULT/log_local': value => '1';
    'DISCOVERY/server':  value => $contrail::contrail_private_vip;
    'IFMAP/certs_store': value => ' ';
    'IFMAP/password':    value => "${contrail::address}.dns";
    'IFMAP/user':        value => "${contrail::address}.dns";
  }

  ini_setting { 'control-fdlimit':
    ensure  => present,
    path    => '/etc/contrail/supervisord_control.conf',
    section => 'supervisord',
    setting => 'minfds',
    value   => '10240',
    require => Package['contrail-control'],
    notify  => Service['supervisor-control'],
  }

  file { '/etc/contrail/dns/contrail-named.conf':
    content => template('contrail/contrail-named.conf.erb'),
    require => Package['contrail-dns'],
  }

  file { '/etc/contrail/dns/contrail-rndc.conf':
    source  => 'puppet:///modules/contrail/contrail-rndc.conf',
    require => Package['contrail-dns'],
  }

  contrail_control_nodemgr_config {
    'DISCOVERY/server': value => $contrail::contrail_private_vip;
    'DISCOVERY/port':   value => '5998';
  }

# Control service
  service { 'contrail-named':
    ensure    => running,
    require   => Package['contrail-dns'],
    subscribe => [
      File['/etc/contrail/dns/contrail-named.conf'],
      File['/etc/contrail/dns/contrail-rndc.conf'],
      ]
  }
  service { 'supervisor-control':
    ensure    => $contrail::service_ensure,
    enable    => true,
    require   => [
      Package['contrail-openstack-control'],
      Package['contrail-control']
      ],
  }

  Contrail_control_config <||> ~> Service['supervisor-control']
  Contrail_dns_config <||> ~>     Service['supervisor-control']

}
