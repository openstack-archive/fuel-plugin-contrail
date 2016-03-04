#    Copyright 2016 Mirantis, Inc.
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

class contrail::compute::vmware {

# Install vCenter-specific contrail packages
  package { ['libxml-commons-external-java', 'libxml-commons-resolver1.1-java', 'libxerces2-java',
            'libslf4j-java', 'libnetty-java', 'libjline-java', 'libzookeeper-java']: } ->
  package { 'contrail-install-vcenter-plugin': } ->
  package { ['libcontrail-java-api','libcontrail-vijava','libcontrail-vrouter-java-api']: } ->
  package { 'contrail-vcenter-plugin': }

# Add user and group
  group { 'contrail':
    ensure => 'present',
  }

  user { 'contrail':
    ensure => 'present',
    home   => '/var/lib/contrail',
    groups => 'contrail',
    shell  => '/bin/false',
    require => Group['contrail'],
  }

# Config file
  file { '/etc/contrail':
    ensure  => directory,
    mode    => '0750',
    owner   => 'contrail',
    group   => 'contrail',
    require => User['contrail'],
  }

  file {'/etc/contrail/contrail-vcenter-plugin.conf':
    ensure  => present,
    content => template('contrail/contrail-vcenter-plugin.conf.erb'),
    require => [Package['contrail-vcenter-plugin'],File['/etc/contrail']],
  }

#### Todo ####
### Need create file /etc/contrail/ESXiToVRouterIp.map ###################
#  file {'/etc/contrail/ESXiToVRouterIp.map':
#    ensure  => present,
#    content => template('contrail/ESXiToVRouterIp.map.erb'),
#    require => [Package['contrail-vcenter-plugin'],File['/etc/contrail']],
#  }
### Need subscribe service { 'contrail-vcenter-plugin': ##################

# Enable and start service
  service { 'contrail-vcenter-plugin':
    ensure    => running,
    enable    => true,
    subscribe => [Package['contrail-vcenter-plugin'],File['/etc/contrail/contrail-vcenter-plugin.conf']],
  }
}

