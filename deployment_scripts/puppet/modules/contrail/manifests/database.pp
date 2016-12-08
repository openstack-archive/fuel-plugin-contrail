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
    package_name => 'contrail-database-common',
    service_name => 'contrail-database',
  }
  tweaks::ubuntu_service_override { 'zookeeper':
    package_name => 'zookeeper',
  }
  sysctl::value { 'vm.swappiness':
    value => '10'
  }
  if roles_include($contrail::contrail_controller_roles) {
    $cassandra_seeds    = $contrail::primary_contrail_controller_ip
    $cluster_name       = 'Contrail'
    $priv_ip            = $::contrail::address
    $contrail_databases = 'config'
    # Zookeeper

    # this is a remanider from dividing by 255
    # + 1 is to avoid it being 0 if uid is a multiplicator of 255
    $zookeeper_id = $contrail::uid % 255 + 1
    package { 'zookeeper': } ->
    file { '/etc/zookeeper/conf/myid':
      content => "${zookeeper_id}\n",
      require => Package['zookeeper'],
    }

    file { '/etc/zookeeper/conf/zoo.cfg':
      content => template('contrail/zoo.cfg.erb');
    }

    service { 'zookeeper':
      ensure    => running,
      enable    => true,
      require   => Package['contrail-openstack-database'],
      subscribe => [Package['zookeeper'],
                    File['/etc/zookeeper/conf/zoo.cfg'],
                    File['/etc/zookeeper/conf/myid'],
                    ],
    }

    service { 'kafka':
      ensure    => stopped,
      enable    => false,
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

      service { 'zookeeper':
        ensure    => stopped,
        enable    => false,
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
  file { '/var/crashes':
    ensure => directory,
    mode   => '0777',
  } ->
  file { '/etc/cassandra/cassandra.yaml':
    content => template('contrail/cassandra.yaml.erb'),
    owner   => 'cassandra',
    group   => 'cassandra',
  } ->
  file_line { 'JVM_stack_size':
    path  => '/etc/cassandra/cassandra-env.sh',
    line  => 'JVM_OPTS="$JVM_OPTS -Xss512k"',
    match => 'JVM_OPTS=\"\$JVM_OPTS -Xss.*\"',
  }

# Supervisor-database
  contrail_database_nodemgr_config {
    'DEFAULT/hostip':         value => $contrail::address;
    'DEFAULT/contrail_databases': value => $contrail_databases;
    'DEFAULT/minimum_diskGB': value => '4';
    'DISCOVERY/server':       value => $contrail::contrail_private_vip;
    'DISCOVERY/port':         value => '5998';
  }

  service { 'contrail-database':
    ensure    => running,
    enable    => true,
    require   => File[$contrail::cassandra_path],
    subscribe => [Package['contrail-openstack-database'],
      File['/etc/cassandra/cassandra.yaml'],
      File_line['JVM_stack_size'],
    ],
  }

  service { 'supervisor-database':
    ensure    => running,
    enable    => true,
    require   => [Service['contrail-database'],Package['contrail-openstack-database']],
    subscribe => File['/etc/cassandra/cassandra.yaml']
  }

  exec { 'wait_for_cassandra':
    provider  => 'shell',
    command   => "nodetool status|grep ^UN|grep ${contrail::address}",
    tries     => 10, # wait for whole cluster is up: 10 tries every 30 seconds = 5 min
    try_sleep => 30,
  }

  Package['contrail-openstack-database'] -> Contrail_database_nodemgr_config <||>
  Contrail_database_nodemgr_config <||> ~> Service['supervisor-database']
}
