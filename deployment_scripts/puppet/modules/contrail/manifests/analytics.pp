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

class contrail::analytics {

  # Resources defaults
  Package { ensure => present }

  File {
    ensure  => present,
    mode    => '0644',
    owner   => 'contrail',
    group   => 'contrail',
    require => Package['contrail-analytics'],
  }

  if !defined(File['/var/crashes']) {
    file { '/var/crashes':
      ensure => directory,
      mode   => '1777',
    }
  }

  Exec { path => '/usr/bin:/usr/sbin:/bin:/sbin' }

  tweaks::ubuntu_service_override { 'contrail-openstack-analytics':
    package_name => 'contrail-openstack-analytics',
    service_name => 'supervisor-analytics',
  }

  tweaks::ubuntu_service_override { 'contrail-analytics':
    package_name => 'contrail-analytics',
    service_name => 'supervisor-analytics',
  }

  # Packages
  package { 'redis-server': } ->
  package { 'contrail-analytics': }
  package { 'contrail-openstack-analytics': }

  # Analytics config files
  file { '/etc/redis/redis.conf':
    source  => 'puppet:///modules/contrail/redis.conf',
    owner   => 'root',
    group   => 'root',
    require => Package['redis-server'],
  }
  contrail_analytics_api_config {
    'DEFAULTS/api_server':                 value => "${::contrail::contrail_private_vip}:${::contrail::api_server_port}";
    'DEFAULTS/host_ip':                    value => $contrail::address;
    'DEFAULTS/cassandra_server_list':      value => $contrail::analytics_db_list;
    'DEFAULTS/http_server_port':           value => '8090';
    'DEFAULTS/rest_api_port':              value => '9081';
    'DEFAULTS/rest_api_ip':                value => '0.0.0.0';
    'DEFAULTS/log_local':                  value => '1';
    'DEFAULTS/log_level':                  value => 'SYS_NOTICE';
    'DEFAULTS/log_category':               value => ' ';
    'DEFAULTS/log_file':                   value => '/var/log/contrail/contrail-analytics-api.log';
    'DEFAULTS/analytics_data_ttl':         value => '48';
    'DEFAULTS/analytics_config_audit_ttl': value => '-1';
    'DEFAULTS/analytics_statistics_ttl':   value => '-1';
    'DEFAULTS/analytics_flow_ttl':         value => '-1';
    'DEFAULTS/aaa_mode':                   value => 'no-auth';
    'DISCOVERY/disc_server_ip':            value => $contrail::contrail_private_vip;
    'DISCOVERY/disc_server_port':          value => '5998';
    'REDIS/redis_server_port':             value => '6379';
    'REDIS/redis_query_port':              value => '6379';
  }

  contrail_collector_config {
    'DEFAULT/analytics_data_ttl':         value => $contrail::analytics_data_ttl;
    'DEFAULT/analytics_config_audit_ttl': value => $contrail::analytics_config_audit_ttl;
    'DEFAULT/analytics_statistics_ttl':   value => $contrail::analytics_statistics_ttl;
    'DEFAULT/analytics_flow_ttl':         value => $contrail::analytics_flow_ttl;
    'DEFAULT/cassandra_server_list':      value => $contrail::analytics_db_list;
    'DEFAULT/hostip':                     value => $contrail::address;
    'DEFAULT/log_file':                   value => '/var/log/contrail/contrail-collector.log';
    'DEFAULT/log_level':                  value => 'SYS_NOTICE';
    'DEFAULT/log_local':                  value => '1';
    'DEFAULT/syslog_port':                value => '-1';
    'DEFAULT/http_server_port':           value => '8089';
    'DEFAULT/kafka_broker_list':          value => $contrail::kafka_broker_list;
    'COLLECTOR/port':                     value => '8086';
    'DISCOVERY/server':                   value => $contrail::contrail_private_vip;
    'REDIS/port':                         value => '6379';
    'REDIS/server':                       value => '127.0.0.1';
  }

  contrail_query_engine_config {
    'DEFAULT/cassandra_server_list': value => $contrail::analytics_db_list;
    'DEFAULT/collectors':            value => '127.0.0.1:8086';
    'DEFAULT/hostip':                value => '$__contrail_host_ip__';
    'DEFAULT/http_server_port':      value => '8091';
    'DEFAULT/log_file':              value => '/var/log/contrail/contrail-query-engine.log';
    'DEFAULT/log_level':             value => 'SYS_NOTICE';
    'DEFAULT/log_local':             value => '1';
    'REDIS/port':                    value => '6379';
    'REDIS/server':                  value => '127.0.0.1';
  }

  contrail_analytics_nodemgr_config {
    'DISCOVERY/server': value => $contrail::contrail_private_vip;
    'DISCOVERY/port':   value => '5998';
  }

  contrail_snmp_collector_config {
    'DEFAULTS/log_local':         value => '1';
    'DEFAULTS/log_level':         value => 'SYS_NOTICE';
    'DEFAULTS/log_file':          value => '/var/log/contrail/contrail-snmp-collector.log';
    'DEFAULTS/zookeeper':         value => $contrail::zk_server_ip;
    'DISCOVERY/disc_server_ip':   value => $contrail::contrail_private_vip;
    'DISCOVERY/disc_server_port': value => '5998';
  }

  contrail_alarm_gen_config {
    'DEFAULTS/host_ip':           value => $contrail::address;
    'DEFAULTS/log_local':         value => '1';
    'DEFAULTS/log_level':         value => 'SYS_NOTICE';
    'DEFAULTS/log_file':          value => '/var/log/contrail/contrail-alarm-gen.log';
    'DEFAULTS/kafka_broker_list': value => $contrail::kafka_broker_list;
    'DEFAULTS/zk_list':           value => $contrail::zk_server_ip;
    'DISCOVERY/disc_server_ip':   value => $contrail::contrail_private_vip;
    'DISCOVERY/disc_server_port': value => '5998';
    'REDIS/redis_server_port':    value => '6379';
  }

  contrail_topology_config {
    'DEFAULTS/log_local':         value => '1';
    'DEFAULTS/log_level':         value => 'SYS_NOTICE';
    'DEFAULTS/log_file':          value => '/var/log/contrail/contrail-topology.log';
    'DEFAULTS/zookeeper':         value => $contrail::zk_server_ip;
    'DISCOVERY/disc_server_ip':   value => $contrail::contrail_private_vip;
    'DISCOVERY/disc_server_port': value => '5998';
  }

  contrail_keystone_auth_config {
    'KEYSTONE/auth_host':         value => $contrail::keystone_address;
    'KEYSTONE/auth_protocol':     value => $contrail::keystone_protocol;
    'KEYSTONE/auth_port':         value => '35357';
    'KEYSTONE/admin_user':        value => $contrail::neutron_user;
    'KEYSTONE/admin_password':    value => $contrail::service_token;
    'KEYSTONE/admin_tenant_name': value => $contrail::service_tenant;
    'KEYSTONE/insecure':          value => $contrail::keystone_insecure;
  }

  # Supervisor-config
  file { '/etc/contrail/supervisord_analytics.conf':
    content => template('contrail/supervisord_analytics.conf.erb'),
    require => Package['contrail-analytics'],
  }

  $keystone_auth_conf = '--conf_file /etc/contrail/contrail-keystone-auth.conf'
  $analytics_api_conf = '--conf_file /etc/contrail/contrail-analytics-api.conf'
  $alarm_gen_conf     = '--conf_file /etc/contrail/contrail-alarm-gen.conf'
  $collector_conf     = '--conf_file /etc/contrail/contrail-collector.conf'

  ini_setting { 'supervisor-analytics-api':
    ensure  => present,
    path    => '/etc/contrail/supervisord_analytics_files/contrail-analytics-api.ini',
    section => 'program:contrail-analytics-api',
    setting => 'command',
    value   => "/usr/bin/contrail-analytics-api ${analytics_api_conf} ${keystone_auth_conf}",
    require => Package['contrail-analytics'],
  }

  ini_setting { 'supervisor-alarm-gen':
    ensure  => present,
    path    => '/etc/contrail/supervisord_analytics_files/contrail-alarm-gen.ini',
    section => 'program:contrail-alarm-gen',
    setting => 'command',
    value   => "/usr/bin/contrail-alarm-gen ${alarm_gen_conf} ${keystone_auth_conf}",
    require => Package['contrail-analytics'],
  }

  ini_setting { 'supervisor-collector':
    ensure  => present,
    path    => '/etc/contrail/supervisord_analytics_files/contrail-collector.ini',
    section => 'program:contrail-collector',
    setting => 'command',
    value   => "/usr/bin/contrail-collector ${collector_conf} ${keystone_auth_conf}",
    require => Package['contrail-analytics'],
  }

# Services
  service { 'redis-server':
    ensure    => running,
    enable    => true,
    require   => Package['redis-server'],
    subscribe => File['/etc/redis/redis.conf'],
  }

  service { 'supervisor-analytics':
    ensure  => $contrail::service_ensure,
    enable  => true,
    require => [
      Package['contrail-openstack-analytics'],
      Service['redis-server'],
      File['/etc/contrail/supervisord_analytics.conf'],
      Ini_setting['supervisor-analytics-api'],
      Ini_setting['supervisor-alarm-gen'],
      Ini_setting['supervisor-collector'],
    ],
  }

  # Cron job for transfer contrail-logs to Fuel master
  # Runs on primary analytics node
  if roles_include('primary-contrail-analytics') {
    file { 'contrailsyslog.sh':
      ensure  => 'present',
      path    => '/usr/local/sbin/contrailsyslog.sh',
      mode    => '0700',
      owner   => 'root',
      group   => 'root',
      content => template('contrail/contrailsyslog.sh.erb'),
    }

    cron { 'contrail-syslog':
      command => '/usr/local/sbin/contrailsyslog.sh',
      user    => 'root',
      minute  => '*/1',
      require => [
        Service['supervisor-analytics'],
        File['contrailsyslog.sh'],
      ],
    }
  }
  Contrail_analytics_nodemgr_config <||> ~> Service['supervisor-analytics']
  Contrail_topology_config <||> ~>          Service['supervisor-analytics']
  Contrail_keystone_auth_config <||> ~>     Service['supervisor-analytics']
  Contrail_snmp_collector_config <||> ~>    Service['supervisor-analytics']
  Contrail_query_engine_config <||> ~>      Service['supervisor-analytics']
  Contrail_analytics_api_config <||> ~>     Service['supervisor-analytics']
  Contrail_collector_config <||> ~>         Service['supervisor-analytics']
  Contrail_alarm_gen_config <||> ~>         Service['supervisor-analytics']
}
