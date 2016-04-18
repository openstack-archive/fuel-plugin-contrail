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

  Package { ensure => installed }

  #Create a pinning
  $vcenter_compute_pkgs = [
    'nova-compute', 'nova-compute-kvm',
    'nova-common', 'nova-compute-libvirt',
    'python-novaclient', 'python-bitstring',
    'tzdata','openjdk-7-jre-headless']
    
  apt::pin { 'favor_contrail_packages':
    priority => 1400,
    label    => 'contrail',
    packages => $vcenter_compute_pkgs
  } ->
  exec { 'fix wrong tzdata':
    command => 'apt-get install tzdata -y --force-yes',
    path    => '/bin:/sbin:/usr/bin:/usr/sbin',
    unless  => "apt-cache policy tzdata | grep '*' -A 2 | grep contrail"
  } ->
  package { $vcenter_compute_pkgs: }

# Install vCenter-specific contrail packages
  package { ['libxml-commons-external-java', 'libxml-commons-resolver1.1-java', 'libxerces2-java',
            'libslf4j-java', 'libnetty-java', 'libjline-java', 'libzookeeper-java']: } ->
  exec { 'contrail-install-vcenter-plugin': } ->
  package { ['libcontrail-java-api','libcontrail-vijava','libcontrail-vrouter-java-api']: } ->
  package { 'contrail-vcenter-plugin': }

# Config file
  file { '/etc/contrail':
    ensure  => directory,
    mode    => '0750',
  } ->
  file {'/etc/contrail/contrail-vcenter-plugin.conf':
    ensure  => present,
    content => template('contrail/contrail-vcenter-plugin.conf.erb'),
    require => [Package['contrail-vcenter-plugin'],File['/etc/contrail']],
  }

# Enable and start service
  service { 'contrail-vcenter-plugin':
    ensure    => running,
    enable    => true,
    subscribe => [Package['contrail-vcenter-plugin'],File['/etc/contrail/contrail-vcenter-plugin.conf']],
  }

}
