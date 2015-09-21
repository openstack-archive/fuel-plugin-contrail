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
#
#    This class installs IF-MAP server for Contrail.

class contrail::cfgm {

# Resources defaults
  Package { ensure => present }

  Exec {
    provider => 'shell',
    path     => '/usr/bin:/usr/sbin',
  }

  File {
    ensure  => present,
    mode    => '0644',
    owner   => 'contrail',
    group   => 'contrail',
    require => Package['contrail-openstack-config'],
  }

# Packages
  package { 'openjdk-7-jre-headless': }->
  package { 'ifmap-server': }->
  package { 'contrail-config': }->
  package { 'contrail-openstack-config': }->

# Java support files
  file {'/etc/java-7-openjdk/security/java.security':
    owner   => 'root',
    group   => 'root',
    source  => 'puppet:///modules/contrail/java.security',
    require => Package['openjdk-7-jre-headless'],
  }

  file { '/etc/ifmap-server/log4j.properties':
    owner   => 'root',
    group   => 'root',
    source  => 'puppet:///modules/contrail/log4j.properties',
    require => Package['openjdk-7-jre-headless'],
  }

  exec { 'update-alternatives-java7':
    command => 'update-java-alternatives --set java-1.7.0-openjdk-amd64',
    unless  => 'test /etc/alternatives/java -ef /usr/lib/jvm/java-7-openjdk-amd64/jre/bin/java',
    require => Package['openjdk-7-jre-headless'],
  }

# Contrail config files
  file { '/etc/ifmap-server/publisher.properties':
    owner   => 'root',
    group   => 'root',
    source  => 'puppet:///modules/contrail/publisher.properties',
    require => Package['ifmap-server'],
  } ->

  file { '/etc/ifmap-server/basicauthusers.properties':
    owner   => 'root',
    group   => 'root',
    content => template('contrail/basicauthusers.properties.erb'),
  }

  file { '/etc/contrail/vnc_api_lib.ini':
    content => template('contrail/vnc_api_lib.ini.erb')
  }

  file { '/etc/contrail/contrail-api.conf':
    content => template('contrail/contrail-api.conf.erb'),
  }

  file { '/etc/contrail/contrail-discovery.conf':
    content => template('contrail/contrail-discovery.conf.erb'),
  }

  file { '/etc/contrail/contrail-keystone-auth.conf':
    content => template('contrail/contrail-keystone-auth.conf.erb'),
  }

  file { '/etc/contrail/contrail-schema.conf':
    content => template('contrail/contrail-schema.conf.erb'),
  }

  file { '/etc/contrail/contrail-svc-monitor.conf':
    content => template('contrail/contrail-svc-monitor.conf.erb'),
  }

  file { '/etc/contrail/contrail-device-manager.conf':
    content => template('contrail/contrail-device-manager.conf.erb')
  }

  file { '/etc/contrail/contrail-config-nodemgr.conf':
    content => template('contrail/contrail-config-nodemgr.conf.erb')
  }
# Supervisor-config
  file { '/etc/contrail/supervisord_config.conf':
    source  => 'puppet:///modules/contrail/supervisord_config.conf',
  }

# Contrail services
# Rabbitmq service disabled
  service {'supervisor-support-service':
    ensure  => stopped,
    enable  => false,
    require => Package['contrail-openstack-config'],
  }
# Neutron-server disabled here
  service {'neutron-server':
    ensure  => stopped,
    enable  => false,
    require => Package['contrail-openstack-config'],
  }

  service { 'supervisor-config':
    ensure    => running,
    enable    => true,
    require   => Package['contrail-openstack-config'],
    subscribe => [File['/etc/contrail/contrail-api.conf'],
                  File['/etc/contrail/contrail-discovery.conf'],
                  File['/etc/contrail/contrail-keystone-auth.conf'],
                  File['/etc/contrail/contrail-schema.conf'],
                  File['/etc/contrail/contrail-svc-monitor.conf'],
                  File['/etc/contrail/contrail-device-manager.conf'],
                  File['/etc/contrail/contrail-config-nodemgr.conf'],
                  File['/etc/contrail/supervisord_config.conf'],
                  File['/etc/ifmap-server/basicauthusers.properties']],
  }

}
