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

class contrail::config {

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
  }

  if !defined(File['/var/crashes']) {
    file { '/var/crashes':
      ensure => directory,
      mode   => '1777',
    }
  }

  class { '::memcached':
    listen_ip  => '127.0.0.1',
    max_memory => '10%',
    item_size  => '10m',
  }

  tweaks::ubuntu_service_override { 'contrail-openstack-config':
    package_name => 'contrail-openstack-config',
    service_name => 'supervisor-config',
  }

  tweaks::ubuntu_service_override { 'contrail-config':
    package_name => 'contrail-config',
    service_name => 'supervisor-config',
  }

# Packages
  if !defined(Package['openjdk-7-jre-headless']) {
    package { 'openjdk-7-jre-headless':
      notify => Package['ifmap-server'],
    }
  }
  package { 'ifmap-server': } ->
  package { 'contrail-config': }
  package { 'contrail-openstack-config': } ->

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

  contrail_api_config {
    'DEFAULTS/ifmap_server_ip':           value => $contrail::address;
    'DEFAULTS/ifmap_server_port':         value => '8443';
    'DEFAULTS/ifmap_username':            value => 'api-server';
    'DEFAULTS/ifmap_password':            value => 'api-server';
    'DEFAULTS/cassandra_server_list':     value => $contrail::contrail_db_list_9160;
    'DEFAULTS/listen_ip_addr':            value => '0.0.0.0';
    'DEFAULTS/listen_port':               value => '9100';
    'DEFAULTS/aaa_mode':                  value => $contrail::aaa_mode;
    'DEFAULTS/cloud_admin_role':          value => 'admin';
    'DEFAULTS/log_file':                  value => '/var/log/contrail/contrail-api.log';
    'DEFAULTS/log_local':                 value => '1';
    'DEFAULTS/log_level':                 value => 'SYS_NOTICE';
    'DEFAULTS/disc_server_ip':            value => $contrail::contrail_private_vip;
    'DEFAULTS/disc_server_port':          value => '5998';
    'DEFAULTS/zk_server_ip':              value => $contrail::zk_server_ip;
    'DEFAULTS/redis_server_ip':           value => '$__contrail_redis_ip__';
    'DEFAULTS/rabbit_server':             value => $contrail::contrail_private_vip;
    'DEFAULTS/rabbit_port':               value => '5673';
    'DEFAULTS/list_optimization_enabled': value => true;
    'DEFAULTS/auth':                      value => 'keystone';
    'DEFAULTS/rabbit_user':               value => 'nova';
    'DEFAULTS/rabbit_password':           value => $contrail::rabbit_password;
    'SECURITY/use_certs':                 value => false;
    'SECURITY/keyfile':                   value => '/etc/contrail/ssl/private_keys/apiserver_key.pem';
    'SECURITY/certfile':                  value => '/etc/contrail/ssl/certs/apiserver.pem';
    'SECURITY/ca_certs':                  value => '/etc/contrail/ssl/certs/ca.pem';
  }

  contrail_api_ini_config {
    'program:contrail-api/command':         value => '/usr/bin/contrail-api --conf_file /etc/contrail/contrail-api.conf --conf_file /etc/contrail/contrail-keystone-auth.conf --worker_id %(process_num)s --listen_port 9100';
    'program:contrail-api/numprocs':        value => '1';
    'program:contrail-api/process_name':    value => '%(process_num)s';
    'program:contrail-api/redirect_stderr': value => true;
    'program:contrail-api/stdout_logfile':  value => '/var/log/contrail/contrail-api-%(process_num)s-stdout.log';
    'program:contrail-api/stderr_logfile':  value => '/dev/null';
    'program:contrail-api/priority':        value => '440';
    'program:contrail-api/autostart':       value => true;
    'program:contrail-api/killasgroup':     value => true;
    'program:contrail-api/stopsignal':      value => 'KILL';
    'program:contrail-api/exitcodes':       value => '0';
    'program:contrail-api/user':            value => 'contrail';
  }

  contrail_discovery_config {
    'DEFAULTS/zk_server_ip':          value => $contrail::contrail_mgmt_vip;
    'DEFAULTS/zk_server_port':        value => '2181';
    'DEFAULTS/listen_ip_addr':        value => '0.0.0.0';
    'DEFAULTS/listen_port':           value => '9110';
    'DEFAULTS/log_local':             value => '1';
    'DEFAULTS/log_file':              value => '/var/log/contrail/discovery.log';
    'DEFAULTS/log_level':             value => 'SYS_NOTICE';
    'DEFAULTS/cassandra_server_list': value => $contrail::contrail_db_list_9160;
    'DEFAULTS/ttl_min':               value => '300';
    'DEFAULTS/ttl_max':               value => '1800';
    'DEFAULTS/hc_interval':           value => '5';
    'DEFAULTS/hc_max_miss':           value => $contrail::discovery_hc_max_miss;
    'DEFAULTS/ttl_short':             value => '1';
    'DNS-SERVER/policy':              value => 'fixed';
  }

  contrail_discovery_ini_config {
    'program:contrail-discovery/command':         value => '/usr/bin/contrail-discovery --conf_file /etc/contrail/contrail-discovery.conf --worker_id %(process_num)s';
    'program:contrail-discovery/numprocs':        value => '1';
    'program:contrail-discovery/process_name':    value => '%(process_num)s';
    'program:contrail-discovery/redirect_stderr': value => true;
    'program:contrail-discovery/stdout_logfile':  value => '/var/log/contrail/contrail-discovery-%(process_num)s-stdout.log';
    'program:contrail-discovery/stderr_logfile':  value => '/dev/null';
    'program:contrail-discovery/priority':        value => '440';
    'program:contrail-discovery/autostart':       value => true;
    'program:contrail-discovery/killasgroup':     value => true;
    'program:contrail-discovery/stopsignal':      value => 'KILL';
    'program:contrail-discovery/exitcodes':       value => '123';
    'program:contrail-discovery/startretries':    value => '10';
    'program:contrail-discovery/user':            value => 'contrail';
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

  if str2bool($contrail::memcached_enabled) {
    contrail_keystone_auth_config {
      'KEYSTONE/memcache_servers':  value => '127.0.0.1:11211';
    }
  }
  else {
    contrail_keystone_auth_config { 'KEYSTONE/memcache_servers':
      ensure => absent,
    }
  }

  contrail_schema_config {
    'DEFAULTS/ifmap_server_ip':       value => $contrail::address;
    'DEFAULTS/ifmap_server_port':     value => '8443';
    'DEFAULTS/ifmap_username':        value => 'schema-transformer';
    'DEFAULTS/ifmap_password':        value => 'schema-transformer';
    'DEFAULTS/api_server_ip':         value => $contrail::contrail_mgmt_vip;
    'DEFAULTS/api_server_port':       value => $contrail::api_server_port;
    'DEFAULTS/zk_server_ip':          value => $contrail::zk_server_ip;
    'DEFAULTS/log_file':              value => '/var/log/contrail/contrail-schema.log';
    'DEFAULTS/cassandra_server_list': value => $contrail::contrail_db_list_9160;
    'DEFAULTS/disc_server_ip':        value => $contrail::contrail_private_vip;
    'DEFAULTS/disc_server_port':      value => '5998';
    'DEFAULTS/log_local':             value => '1';
    'DEFAULTS/log_level':             value => 'SYS_NOTICE';
    'DEFAULTS/rabbit_server':         value => $contrail::contrail_private_vip;
    'DEFAULTS/rabbit_port':           value => '5673';
    'DEFAULTS/rabbit_user':           value => 'nova';
    'DEFAULTS/rabbit_password':       value => $contrail::rabbit_password;
    'SECURITY/use_certs':             value => false;
    'SECURITY/keyfile':               value => '/etc/contrail/ssl/private_keys/schema_xfer_key.pem';
    'SECURITY/certfile':              value => '/etc/contrail/ssl/certs/schema_xfer.pem';
    'SECURITY/ca_certs':              value => '/etc/contrail/ssl/certs/ca.pem';
  }

  contrail_svc_monitor_config {
    'DEFAULTS/ifmap_server_ip':        value => $contrail::address;
    'DEFAULTS/ifmap_server_port':      value => '8443';
    'DEFAULTS/ifmap_username':         value => 'svc-monitor';
    'DEFAULTS/ifmap_password':         value => 'svc-monitor';
    'DEFAULTS/api_server_ip':          value => $contrail::contrail_mgmt_vip;
    'DEFAULTS/api_server_port':        value => $contrail::api_server_port;
    'DEFAULTS/zk_server_ip':           value => $contrail::zk_server_ip;
    'DEFAULTS/log_file':               value => '/var/log/contrail/contrail-svc-monitor.log';
    'DEFAULTS/cassandra_server_list':  value => $contrail::contrail_db_list_9160;
    'DEFAULTS/region':                 value => $contrail::region;
    'DEFAULTS/disc_server_ip':         value => $contrail::contrail_private_vip;
    'DEFAULTS/disc_server_port':       value => '5998';
    'DEFAULTS/log_local':              value => '1';
    'DEFAULTS/log_level':              value => 'SYS_NOTICE';
    'DEFAULTS/rabbit_server':          value => $contrail::contrail_private_vip;
    'DEFAULTS/rabbit_port':            value => '5673';
    'DEFAULTS/rabbit_user':            value => 'nova';
    'DEFAULTS/rabbit_password':        value => $contrail::rabbit_password;
    'SECURITY/use_certs':              value => false;
    'SECURITY/keyfile':                value => '/etc/contrail/ssl/private_keys/svc_monitor_key.pem';
    'SECURITY/certfile':               value => '/etc/contrail/ssl/certs/svc_monitor.pem';
    'SECURITY/ca_certs':               value => '/etc/contrail/ssl/certs/ca.pem';
    'SCHEDULER/analytics_server_ip':   value => $contrail::contrail_mgmt_vip;
    'SCHEDULER/analytics_server_port': value => '8081';
  }

  contrail_device_manager_config {
    'DEFAULTS/api_server_ip':         value => $contrail::contrail_mgmt_vip;
    'DEFAULTS/api_server_port':       value => $contrail::api_server_port;
    'DEFAULTS/zk_server_ip':          value => $contrail::zk_server_ip;
    'DEFAULTS/log_file':              value => '/var/log/contrail/contrail-device-manager.log';
    'DEFAULTS/cassandra_server_list': value => $contrail::contrail_db_list_9160;
    'DEFAULTS/disc_server_ip':        value => $contrail::contrail_private_vip;
    'DEFAULTS/disc_server_port':      value => '5998';
    'DEFAULTS/log_local':             value => '1';
    'DEFAULTS/log_level':             value => 'SYS_NOTICE';
    'DEFAULTS/rabbit_server':         value => $contrail::contrail_private_vip;
    'DEFAULTS/rabbit_port':           value => '5673';
    'DEFAULTS/rabbit_user':           value => 'nova';
    'DEFAULTS/rabbit_password':       value => $contrail::rabbit_password;
  }

  contrail_config_nodemgr_config {
    'DISCOVERY/server': value => $contrail::contrail_private_vip;
    'DISCOVERY/port':   value => '5998';
  }

# Supervisor-config
  file { '/etc/contrail/supervisord_config.conf':
    content  => template('contrail/supervisord_config.conf.erb'),
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
    ensure    => $contrail::service_ensure,
    enable    => true,
    require   => [Package['contrail-openstack-config'],Package['contrail-config']],
    subscribe => [
      File['/etc/contrail/supervisord_config.conf'],
      File['/etc/ifmap-server/basicauthusers.properties'],
      Package['contrail-openstack-config'],
      ],
  }

  Package['contrail-config'] ->          Contrail_api_ini_config <||>
  Package['contrail-config'] ->          Contrail_discovery_ini_config <||>
  Contrail_api_ini_config <||> ~>        Service['supervisor-config']
  Contrail_discovery_ini_config <||> ~>  Service['supervisor-config']
  Contrail_svc_monitor_config <||> ~>    Service['supervisor-config']
  Contrail_schema_config <||> ~>         Service['supervisor-config']
  Contrail_discovery_config <||> ~>      Service['supervisor-config']
  Contrail_config_nodemgr_config <||> ~> Service['supervisor-config']
  Contrail_api_config <||> ~>            Service['supervisor-config']
  Contrail_device_manager_config <||> ~> Service['supervisor-config']
  Contrail_keystone_auth_config <||> ~>  Service['supervisor-config']
}
