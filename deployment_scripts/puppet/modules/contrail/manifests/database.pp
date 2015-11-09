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
  package { 'zookeeper': } ->
  package { 'cassandra': } ->
  package { 'contrail-openstack-database': }

# Zookeeper
  file { '/etc/zookeeper/conf/myid':
    content => $contrail::uid,
    require => Package['zookeeper'],
  }

  file { '/etc/zookeeper/conf/zoo.cfg':
    content => template('contrail/zoo.cfg.erb');
  }

  service { 'zookeeper':
    ensure    => running,
    enable    => true,
    require   => [Package['zookeeper'],Package['contrail-openstack-database']],
    subscribe => [File['/etc/zookeeper/conf/zoo.cfg'],
                  File['/etc/zookeeper/conf/myid'],
                  ],
  }

# Cassandra
  file { '/var/lib/cassandra':
    ensure  => directory,
    mode    => '0755',
    owner   => 'cassandra',
    group   => 'cassandra',
    require => Package['cassandra'],
  }
  file { '/var/crashes':
    ensure => directory,
    mode   => '0777',
  }
  file { '/etc/cassandra/cassandra.yaml':
    content => template('contrail/cassandra.yaml.erb'),
  }
  file { '/etc/cassandra/cassandra-env.sh':
    source  => 'puppet:///modules/contrail/cassandra-env.sh',
  }

# Supervisor-database
  file { '/etc/contrail/contrail-database-nodemgr.conf':
    content => template('contrail/contrail-database-nodemgr.conf.erb'),
  }

  service { 'contrail-database':
    ensure => running,
    enable => true,
    require => [File['/var/lib/cassandra'],Package['contrail-openstack-database']],
    subscribe   => [
      File['/etc/cassandra/cassandra.yaml'],
      File['/etc/cassandra/cassandra-env.sh'],
    ],
  }

  service { 'supervisor-database':
    ensure      => running,
    enable      => true,
    require     => [Service['contrail-database'],Package['contrail-openstack-database']],
    subscribe   => [
      File['/etc/cassandra/cassandra.yaml'],
      File['/etc/contrail/contrail-database-nodemgr.conf'],
    ],
  }

  notify{"Waiting for cassandra seed node":} ->
  exec {'wait_for_cassandra_seed':
    provider  => 'shell',
    command   => "nodetool status|grep ^UN|grep ${contrail::cassandra_seed_ip}",
    tries     => 10, # wait for whole cluster is up: 10 tries every 30 seconds = 5 min
    try_sleep => 30,
    require   => Service['supervisor-database'],
  }

  notify{"Waiting for cassandra":} ->
  exec {'wait_for_cassandra':
    provider  => 'shell',
    command   => "nodetool status|grep ^UN|grep ${contrail::address}",
    tries     => 10, # wait for whole cluster is up: 10 tries every 30 seconds = 5 min
    try_sleep => 30,
    require   => Service['supervisor-database'],
  }
}
