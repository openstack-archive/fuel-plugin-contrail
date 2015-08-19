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

  File {
    ensure  => present,
    mode    => '0644',
    owner   => root,
    group   => root,
    require => Package['contrail-openstack-config'],
  }

  Exec { path => '/usr/bin:/usr/sbin:/bin:/sbin' }

# Packages
  package { 'openjdk-7-jre-headless': }->
  package { 'ifmap-server': }->
  package { 'contrail-openstack-config': }->

# Java support files
  file {'/etc/java-7-openjdk/security/java.security':
    source  => 'puppet:///modules/contrail/java.security',
    require => Package['openjdk-7-jre-headless'],
  }

  file { '/etc/ifmap-server/log4j.properties':
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
    source  => 'puppet:///modules/contrail/publisher.properties',
    require => Package['ifmap-server'],
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

  file { '/etc/ifmap-server/basicauthusers.properties':
    content => template('contrail/basicauthusers.properties.erb'),
  }

# Contrail services
# Rabbitmq service disabled
  service {'supervisor-support-service':
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
                 File['/etc/ifmap-server/basicauthusers.properties']],
  }

}
