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

class contrail::webui {

# Resources defaults
  Package { ensure => present }

  File {
    ensure  => present,
    mode    => '0644',
    owner   => 'contrail',
    group   => 'contrail',
    require => Package['contrail-openstack-webui'],
  }

# Packages
  package { 'nodejs': } ->
  package { 'redis-server': } ->
  package { 'contrail-web-core': } ->
  package { 'contrail-web-controller': } ->
  package { 'contrail-openstack-webui': }

# Webui config files
  file { '/etc/contrail/config.global.js':
    content => template('contrail/config.global.js.erb'),
  }

  file { '/etc/contrail/contrail-webui-userauth.js':
    content => template('contrail/contrail-webui-userauth.js.erb'),
  }

# Services
  ## US251186: With redis-server package version 2:2.8.4-2,
  ##           service does not start automatically upon install.
  service { 'redis-server':
    ensure    => running,
    enable    => true,
    require   => Package['redis-server'],
  }

  service { 'supervisor-webui':
    ensure    => running,
    enable    => true,
    require   => Package['contrail-openstack-webui'],
    subscribe => [
      File['/etc/contrail/contrail-webui-userauth.js'],
      File['/etc/contrail/config.global.js'],
      ],
  }

}