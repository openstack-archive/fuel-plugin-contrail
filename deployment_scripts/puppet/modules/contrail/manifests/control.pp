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
  }

  Exec {
    provider => 'shell',
    path     => '/usr/bin:/bin:/sbin',
  }

  tweaks::ubuntu_service_override { 'contrail-openstack-control':
    package_name => 'contrail-openstack-control',
    service_name => 'supervisor-control',
  }

  tweaks::ubuntu_service_override { 'contrail-control':
    package_name => 'contrail-control',
    service_name => 'supervisor-control',
  }

# Packages
  package { 'contrail-dns': }
  package { 'contrail-control': }
  package { 'contrail-openstack-control': }

  contrail_control_config {
    'DEFAULT/hostip':                  value => $contrail::address;
    'DEFAULT/hostname':                value => $::fqdn;
    'DEFAULT/log_file':                value => '/var/log/contrail/contrail-control.log';
    'DEFAULT/log_level':               value => 'SYS_NOTICE';
    'DEFAULT/log_local':               value => '1';
    'DEFAULT/sandesh_send_rate_limit': value => $contrail::sandesh_send_rate_limit;
    'DISCOVERY/server':                value => $contrail::contrail_private_vip;
    'IFMAP/certs_store':               value => ' ';
    'IFMAP/password':                  value => $contrail::address;
    'IFMAP/user':                      value => $contrail::address;
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

  if $::contrail::tls_xmpp_enable {

    file { '/etc/contrail/ssl/':
      ensure => directory,
      owner  => 'contrail',
      group  => 'contrail',
      tag    => 'tls_xmpp',
    }

    file { '/etc/contrail/ssl/xmpp_wildcard.crt':
      content => $contrail::tls_xmpp_wildcard_crt,
      owner   => 'contrail',
      group   => 'contrail',
      tag     => 'tls_xmpp',
    }

    file { '/etc/contrail/ssl/xmpp_wildcard.key':
      content => $contrail::tls_xmpp_wildcard_key,
      owner   => 'contrail',
      group   => 'contrail',
      tag     => 'tls_xmpp',
    }

    file { '/etc/contrail/ssl/xmpp_ca.crt':
      content => $contrail::tls_xmpp_ca_crt,
      owner   => 'contrail',
      group   => 'contrail',
      tag     => 'tls_xmpp',
    }

    contrail_control_config {
      'DEFAULT/xmpp_auth_enable': value => 'True';
      'DEFAULT/xmpp_server_cert': value => '/etc/contrail/ssl/xmpp_wildcard.crt';
      'DEFAULT/xmpp_server_key':  value => '/etc/contrail/ssl/xmpp_wildcard.key';
      'DEFAULT/xmpp_ca_cert':     value => '/etc/contrail/ssl/xmpp_ca.crt';
    }

    contrail_dns_config {
      'DEFAULT/xmpp_dns_auth_enable': value => 'True';
      'DEFAULT/xmpp_server_cert': value => '/etc/contrail/ssl/xmpp_wildcard.crt';
      'DEFAULT/xmpp_server_key':  value => '/etc/contrail/ssl/xmpp_wildcard.key';
      'DEFAULT/xmpp_ca_cert':     value => '/etc/contrail/ssl/xmpp_ca.crt';
    }

    Package['contrail-control'] -> File<| tag == 'tls_xmpp' |>  ->  Contrail_control_config <||> ~> Service['supervisor-control']
    Package['contrail-dns'] -> File<| tag == 'tls_xmpp' |>  ->  Contrail_dns_config <||> ~> Service['supervisor-control']
  }

  # Supervisor-config
  file { '/etc/contrail/supervisord_control.conf':
    content => template('contrail/supervisord_control.conf.erb'),
    require => Package['contrail-control'],
  }

  contrail_control_nodemgr_config {
    'DISCOVERY/server': value => $contrail::contrail_private_vip;
    'DISCOVERY/port':   value => '5998';
  }

  service { 'contrail-dns':
    ensure  => running,
    require => Package['contrail-dns'],
  }

  service { 'contrail-named':
    ensure    => running,
    require   => Package['contrail-dns'],
    subscribe => [
      Package['contrail-dns'],
      ]
  }

  service { 'supervisor-control':
    ensure    => $contrail::service_ensure,
    enable    => true,
    subscribe => [Package['contrail-openstack-control'], Package['contrail-control']],
    require   => [
      File['/etc/contrail/supervisord_control.conf'],
      Package['contrail-openstack-control'],
      Package['contrail-control']
      ],
  }

  Contrail_control_config <||>  ~> Service['supervisor-control']
  Contrail_dns_config <||>      ~> Service['supervisor-control']
  Contrail_dns_config <||>      ~> Service['contrail-dns']
}
