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
    owner   => root,
    group   => root,
    require => Package['contrail-openstack-analytics'],
  }

  Exec { path => '/usr/bin:/usr/sbin:/bin:/sbin' }

  tweaks::ubuntu_service_override { 'supervisor-analytics':
    package_name => 'contrail-analytics',
  }

# Packages
  package { 'redis-server': } ->
  package { 'contrail-analytics': }
  package { 'contrail-openstack-analytics': }

# Analytics config files
  file { '/etc/redis/redis.conf':
    source  => 'puppet:///modules/contrail/redis.conf',
    require => Package['redis-server'],
  }

  file { '/etc/contrail/contrail-analytics-api.conf':
    content => template('contrail/contrail-analytics-api.conf.erb'),
  }

  file { '/etc/contrail/contrail-collector.conf':
    content => template('contrail/contrail-collector.conf.erb'),
  }

  file { '/etc/contrail/contrail-query-engine.conf':
    content => template('contrail/contrail-query-engine.conf.erb'),
  }

  file { '/etc/contrail/contrail-analytics-nodemgr.conf':
    content => template('contrail/contrail-analytics-nodemgr.conf.erb'),
  }

  file { '/etc/contrail/contrail-snmp-collector.conf':
    content => template('contrail/contrail-snmp-collector.conf.erb'),
  }

  file { '/etc/contrail/contrail-alarm-gen.conf':
    content => template('contrail/contrail-alarm-gen.conf.erb'),
  }

  file { '/etc/contrail/contrail-topology.conf':
    content => template('contrail/contrail-topology.conf.erb'),
  }

  ini_setting { 'analytics-fdlimit':
    ensure  => present,
    path    => '/etc/contrail/supervisord_analytics.conf',
    section => 'supervisord',
    setting => 'minfds',
    value   => '65535',
    require => Package['contrail-analytics'],
  }

  ini_setting { 'contrail-analytics-api-keystone':
    ensure  => present,
    path    => '/etc/contrail/supervisord_analytics_files/contrail-analytics-api.ini',
    section => 'program:contrail-analytics-api',
    setting => 'command',
    value   => '/usr/bin/contrail-analytics-api -c /etc/contrail/contrail-analytics-api.conf -c /etc/contrail/contrail-keystone-auth.conf',
    require => Package['contrail-analytics'],
  }

  ini_setting { 'contrail-alarm-gen-keystone':
    ensure  => present,
    path    => '/etc/contrail/supervisord_analytics_files/contrail-alarm-gen.ini',
    section => 'program:contrail-alarm-gen',
    setting => 'command',
    value   => '/usr/bin/contrail-alarm-gen -c /etc/contrail/contrail-alarm-gen.conf -c /etc/contrail/contrail-keystone-auth.conf',
    require => Package['contrail-analytics'],
  }

  ini_setting { 'contrail-collector-keystone':
    ensure  => present,
    path    => '/etc/contrail/supervisord_analytics_files/contrail-collector.ini',
    section => 'program:contrail-collector',
    setting => 'command',
    value   => '/usr/bin/contrail-collector -c /etc/contrail/contrail-keystone-auth.conf',
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
    ensure    => $contrail::service_ensure,
    enable    => true,
    require   => [Package['contrail-openstack-analytics'],
                    Service['redis-server'],
                    Ini_setting['analytics-fdlimit']],
    subscribe => [File['/etc/contrail/contrail-analytics-api.conf'],
                    File['/etc/contrail/contrail-collector.conf'],
                    File['/etc/contrail/contrail-query-engine.conf'],
                    File['/etc/contrail/contrail-analytics-nodemgr.conf'],
                    File['/etc/contrail/contrail-snmp-collector.conf'],
                    File['/etc/contrail/contrail-alarm-gen.conf'],
                    File['/etc/contrail/contrail-topology.conf'],
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

}
