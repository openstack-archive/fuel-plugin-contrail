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

class contrail::logging(
  $log_level = "INFO",
) {
  ::rsyslog::imfile { "100-contrail-analytics-api":
    file_name     => "/var/log/contrail/contrail-analytics-api.log",
    file_tag      => "contrail-analytics-api",
    file_facility => "syslog",
    file_severity => $log_level,
  }

  ::rsyslog::imfile { "101-contrail-api":
    file_name     => "/var/log/contrail/contrail-api.log",
    file_tag      => "contrail-api",
    file_facility => "syslog",
    file_severity => $log_level,
  }

  ::rsyslog::imfile { "102-contrail-collector":
    file_name     => "/var/log/contrail/contrail-collector.log",
    file_tag      => "contrail-collector",
    file_facility => "syslog",
    file_severity => $log_level,
  }

  ::rsyslog::imfile { "103-contrail-control":
    file_name     => "/var/log/contrail/contrail-control.log",
    file_tag      => "contrail-control",
    file_facility => "syslog",
    file_severity => $log_level,
  }

  ::rsyslog::imfile { "104-contrail-device-manager":
    file_name     => "/var/log/contrail/contrail-device-manager.log",
    file_tag      => "contrail-device-manager",
    file_facility => "syslog",
    file_severity => $log_level,
  }

  ::rsyslog::imfile { "105-contrail-dns":
    file_name     => "/var/log/contrail/contrail-dns.log",
    file_tag      => "contrail-dns",
    file_facility => "syslog",
    file_severity => $log_level,
  }

  ::rsyslog::imfile { "106-contrail-query-engine":
    file_name     => "/var/log/contrail/contrail-query-engine.log",
    file_tag      => "contrail-query-engine",
    file_facility => "syslog",
    file_severity => $log_level,
  }

  ::rsyslog::imfile { "107-contrail-schema":
    file_name     => "/var/log/contrail/contrail-schema.log",
    file_tag      => "contrail-schema",
    file_facility => "syslog",
    file_severity => $log_level,
  }

  ::rsyslog::imfile { "108-contrail-snmp-collector":
    file_name     => "/var/log/contrail/contrail-snmp-collector.log",
    file_tag      => "contrail-snmp-collector",
    file_facility => "syslog",
    file_severity => $log_level,
  }

  ::rsyslog::imfile { "109-contrail-svc-monitor":
    file_name     => "/var/log/contrail/contrail-svc-monitor.log",
    file_tag      => "contrail-svc-monitor",
    file_facility => "syslog",
    file_severity => $log_level,
  }

  ::rsyslog::imfile { "110-contrail-topology":
    file_name     => "/var/log/contrail/contrail-topology.log",
    file_tag      => "contrail-topology",
    file_facility => "syslog",
    file_severity => $log_level,
  }

  ::rsyslog::imfile { "111-contrail-vrouter-agent":
    file_name     => "/var/log/contrail/contrail-vrouter-agent.log",
    file_tag      => "contrail-vrouter-agent",
    file_facility => "syslog",
    file_severity => $log_level,
  }

  ::rsyslog::imfile { "112-contrail-discovery":
    file_name     => "/var/log/contrail/discovery.log",
    file_tag      => "contrail-discovery",
    file_facility => "syslog",
    file_severity => $log_level,
  }

  file { "${::rsyslog::params::rsyslog_d}/100-contrail-analytics-api.conf":
    ensure => present,
    content => template("${module_name}/100-contrail-analytics-api.conf.erb"),
  }

  file { "${::rsyslog::params::rsyslog_d}/101-contrail-api.conf":
    ensure  => present,
    content => template("${module_name}/101-contrail-api.conf.erb"),
  }

  file { "${::rsyslog::params::rsyslog_d}/102-contrail-collector.conf":
    ensure  => present,
    content => template("${module_name}/102-contrail-collector.conf.erb"),
  }

  file { "${::rsyslog::params::rsyslog_d}/103-contrail-control.conf":
    ensure  => present,
    content => template("${module_name}/103-contrail-control.conf.erb"),
  }

  file { "${::rsyslog::params::rsyslog_d}/104-contrail-device-manager.conf":
    ensure  => present,
    content => template("${module_name}/104-contrail-device-manager.conf.erb"),
  }

  file { "${::rsyslog::params::rsyslog_d}/105-contrail-dns.conf":
    ensure  => present,
    content => template("${module_name}/105-contrail-dns.conf.erb"),
  }

  file { "${::rsyslog::params::rsyslog_d}/106-contrail-query-engine.conf":
    ensure  => present,
    content => template("${module_name}/106-contrail-query-engine.conf.erb"),
  }

  file { "${::rsyslog::params::rsyslog_d}/107-contrail-schema.conf":
    ensure  => present,
    content => template("${module_name}/107-contrail-schema.conf.erb"),
  }

  file { "${::rsyslog::params::rsyslog_d}/108-contrail-snmp-collector.conf":
    ensure  => present,
    content => template("${module_name}/108-contrail-snmp-collector.conf.erb"),
  }

  file { "${::rsyslog::params::rsyslog_d}/109-contrail-svc-monitor.conf":
    ensure  => present,
    content => template("${module_name}/109-contrail-svc-monitor.conf.erb"),
  }

  file { "${::rsyslog::params::rsyslog_d}/110-contrail-topology.conf":
    ensure  => present,
    content => template("${module_name}/110-contrail-topology.conf.erb"),
  }

  file { "${::rsyslog::params::rsyslog_d}/111-contrail-vrouter-agent.conf":
    ensure  => present,
    content => template("${module_name}/111-contrail-vrouter-agent.conf.erb"),
  }

  file { "${::rsyslog::params::rsyslog_d}/112-contrail-discovery.conf":
    ensure  => present,
    content => template("${module_name}/112-contrail-discovery.conf.erb"),
  }
}
