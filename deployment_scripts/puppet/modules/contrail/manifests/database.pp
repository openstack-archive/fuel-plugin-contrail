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

class contrail::database {

# Packages
  class { 'contrail::package':
    install => ['contrail-openstack-database','cassandra','zookeeper'],
  }

# Zookeeper
  file { '/etc/zookeeper/conf/myid':
    ensure  => present,
    content => $contrail::uid,
  }
  file { '/etc/zookeeper/conf/zoo.cfg':
    ensure  => present,
    content => template('contrail/zoo.cfg.erb');
  }
  service { 'zookeeper':
  ensure      => running,
  enable      => true,
  require     => Class['contrail::package'],
  subscribe   => [
    File['/etc/zookeeper/conf/zoo.cfg'],
    File['/etc/zookeeper/conf/myid'],
  ],
 }

# Cassandra
  file { '/etc/cassandra/cassandra.yaml':
    ensure  => present,
    content => template('contrail/cassandra.yaml.erb'),
  } ->
  file { '/etc/cassandra/cassandra-env.sh':
    ensure  => present,
    source  => 'puppet:///modules/contrail/cassandra-env.sh',
  } ->
  file { '/var/lib/cassandra':
    ensure  => directory,
    mode    => '0755',
    owner   => root,
    group   => root,
    require => Class['contrail::package'],
  }

# Supervisor-database
  file { '/etc/contrail/contrail-database-nodemgr.conf':
    ensure  => present,
    content => template('contrail/contrail-database-nodemgr.conf.erb'),
  }
  file { '/etc/contrail/supervisord_database.conf':
    ensure  => present,
    source  => 'puppet:///modules/contrail/supervisord_database.conf',
  }
  service { 'supervisor-database':
    ensure      => running,
    enable      => true,
    require     => File['/var/lib/cassandra'],
    subscribe   => [
      File['/etc/cassandra/cassandra.yaml'],
      File['/etc/cassandra/cassandra-env.sh'],
      File['/etc/contrail/contrail-database-nodemgr.conf'],
      File['/etc/contrail/supervisord_database.conf'],
    ],
  }

}