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

  apt::pin { 'contrail-nodejs-pin':
    order    => '101',
    packages => ['nodejs'],
    priority => '1200',
    label    => 'contrail',
    before   => Package['nodejs'],
  }

# Packages
  package { 'nodejs': } ->
  package { 'contrail-web-core': } ->
  package { 'contrail-web-controller': } ->
  package { 'contrail-openstack-webui': }

# Webui config files
  file { '/etc/contrail/config.global.js':
    ensure  => present,
    content => template('contrail/config.global.js.erb'),
    mode    => '0644',
    owner   => 'contrail',
    group   => 'contrail',
    require => Package['contrail-openstack-webui'],
  }

  file { '/etc/contrail/contrail-webui-userauth.js':
    ensure  => present,
    content => template('contrail/contrail-webui-userauth.js.erb'),
    mode    => '0644',
    owner   => 'contrail',
    group   => 'contrail',
    require => Package['contrail-openstack-webui'],
  }

# Services
  service { 'supervisor-webui':
    ensure    => running,
    enable    => true,
    require   => Package['contrail-openstack-webui'],
    subscribe => [
      File['/etc/contrail/contrail-webui-userauth.js'],
      File['/etc/contrail/config.global.js'],
      Package['contrail-openstack-webui'],
      ],
  }
}
