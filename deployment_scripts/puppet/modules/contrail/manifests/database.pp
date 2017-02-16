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

  tweaks::ubuntu_service_override { 'cassandra':
    package_name => 'cassandra',
  }

  tweaks::ubuntu_service_override { 'contrail-database':
    package_name => 'contrail-openstack-database',
  }
  tweaks::ubuntu_service_override { 'zookeeper':
    package_name => 'zookeeper',
  }
  tweaks::ubuntu_service_override { 'supervisor-database':
    package_name => 'contrail-openstack-database',
  }
  if roles_include($contrail::contrail_db_roles) {
    $cassandra_seeds = $contrail::primary_contrail_db_ip
    $cluster_name    = 'Contrail'
    $contrail_databases = 'config'

    # Zookeeper is created only on contrail-db nodes,
    # it is not needed on contrail-analytics-db

    package { 'zookeeper': } ->
    file { '/etc/zookeeper/conf/myid':
      content => $contrail::uid,
      require => Package['zookeeper'],
    }

    file { '/etc/zookeeper/conf/zoo.cfg':
      content => template('contrail/zoo.cfg.erb'),
      require => Package['zookeeper'],
    }

    service { 'zookeeper':
      ensure    => running,
      enable    => true,
      require   => [Package['zookeeper'],Package['contrail-openstack-database']],
      subscribe => [
        File['/etc/zookeeper/conf/zoo.cfg'],
        File['/etc/zookeeper/conf/myid'],
        ],
    }

    #Supervisor-config
    file { '/etc/contrail/supervisord_database.conf':
      content => template('contrail/supervisord_database.conf.erb'),
      before  => Service['supervisor-database'],
    }

    package { 'kafka': } ->
    service { 'kafka':
      ensure    => stopped,
      enable    => false,
      hasstatus => false,
    }

  } elsif roles_include($contrail::analytics_db_roles) {
      $cassandra_seeds = $contrail::primary_analytics_db_ip
      $cluster_name    = 'Analytics'
      $contrail_databases = 'analytics'

      # Kafka
      package { 'kafka': } ->
      file { '/tmp/kafka-logs':
        ensure => 'directory',
        mode   => '0755',
      } ->
      file { '/usr/share/kafka/config/log4j.properties':
        source  => 'puppet:///modules/contrail/kafka-log4j.properties',
        require => Package['kafka'],
      } ->
      file { '/usr/share/kafka/config/server.properties':
        content => template('contrail/kafka-server.properties.erb'),
        require => Package['kafka'],
      } ->
      file { '/tmp/kafka-logs/meta.properties':
        content => inline_template("version=0\nbroker.id=<%= scope.lookupvar('contrail::uid') %>\n");
      }

      service { 'kafka':
        ensure    => running,
        enable    => true,
        require   => Package['kafka'],
        subscribe => [
          File['/usr/share/kafka/config/log4j.properties'],
          File['/usr/share/kafka/config/server.properties'],
          File['/tmp/kafka-logs/meta.properties'],
          ],
      }

      package { 'zookeeper': } ->
      service { 'zookeeper':
        ensure => stopped,
        enable => false,
      }
  }
# Cassandra
  package { 'cassandra': } ->
  package { 'contrail-openstack-database': }

  file { $contrail::cassandra_path:
    ensure  => directory,
    mode    => '0755',
    owner   => 'cassandra',
    group   => 'cassandra',
    require => Package['cassandra'],
  } ->
  file { '/etc/cassandra/cassandra.yaml':
    content => template('contrail/cassandra.yaml.erb'),
    owner   => 'cassandra',
    group   => 'cassandra',
  } ->
  file { '/etc/cassandra/cassandra-env.sh':
    source => 'puppet:///modules/contrail/cassandra-env.sh',
    owner  => 'cassandra',
    group  => 'cassandra',
  } ->
  file { '/etc/security/limits.d/cassandra.conf':
    content => template('contrail/cassandra_limits.conf.erb'),
  }

  if !defined(File['/var/crashes']) {
    file { '/var/crashes':
      ensure  => directory,
      mode    => '0777',
      require => File[$contrail::cassandra_path],
      before  => File['/etc/cassandra/cassandra.yaml']
    }
  }

# Supervisor-database
  contrail_database_nodemgr_config {
    'DEFAULT/hostip':             value => $contrail::address;
    'DEFAULT/contrail_databases': value => $contrail_databases;
    'DEFAULT/minimum_diskGB':     value => '4';
    'DISCOVERY/server':           value => $contrail::contrail_private_vip;
    'DISCOVERY/port':             value => '5998';
  }

  service { 'contrail-database':
    ensure    => running,
    enable    => true,
    require   => [File[$contrail::cassandra_path],Package['contrail-openstack-database']],
    subscribe => [
      File['/etc/cassandra/cassandra.yaml'],
      File['/etc/cassandra/cassandra-env.sh'],
    ],
  }

  service { 'supervisor-database':
    ensure    => running,
    enable    => true,
    require   => [Service['contrail-database'],Package['contrail-openstack-database']],
    subscribe => File['/etc/cassandra/cassandra.yaml']
  }

  $cassandra_seed = $cassandra_seeds[0]
  notify{ 'Waiting for cassandra seed node': } ->
  exec { 'wait_for_cassandra_seed':
    provider  => 'shell',
    command   => "nodetool status|grep ^UN|grep ${cassandra_seed}",
    tries     => 10, # wait for whole cluster is up: 10 tries every 30 seconds = 5 min
    try_sleep => 30,
    require   => Service['supervisor-database'],
  }


  notify{ 'Waiting for cassandra': } ->
  exec { 'wait_for_cassandra':
    provider  => 'shell',
    command   => "nodetool status|grep ^UN|grep ${contrail::address}",
    tries     => 10, # wait for whole cluster is up: 10 tries every 30 seconds = 5 min
    try_sleep => 30,
    require   => Service['supervisor-database'],
  }
  Contrail_database_nodemgr_config <||> ~> Service['supervisor-database']
}
