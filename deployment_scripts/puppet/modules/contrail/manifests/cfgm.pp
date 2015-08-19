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
  }

  Exec { path => '/usr/bin:/usr/sbin:/bin:/sbin' }

  package { 'openjdk-7-jre-headless': }->
  package { 'contrail-openstack-config': }->
  package { 'ifmap-server': }->

  file {'/etc/java-7-openjdk/security/java.security':
    source  => 'puppet:///modules/contrail/java.security',
  }->

  file { '/etc/ifmap-server/log4j.properties':
    source  => 'puppet:///modules/contrail/log4j.properties',
  }->

  file { '/etc/ifmap-server/publisher.properties':
    source  => 'puppet:///modules/contrail/publisher.properties',
  }

  exec { 'update-alternatives-java7':
    command => 'update-java-alternatives --set java-1.7.0-openjdk-amd64',
    unless  => 'test /etc/alternatives/java -ef /usr/lib/jvm/java-7-openjdk-amd64/jre/bin/java',
  }
}
