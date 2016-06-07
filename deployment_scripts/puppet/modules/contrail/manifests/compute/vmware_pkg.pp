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

class contrail::compute::vmware_pkg {

  $patch_path  = '/usr/lib/python2.7/dist-packages'

  Package {
    ensure => installed,
  }

  Exec {
    path => ['/usr/local/sbin', '/usr/local/bin', '/usr/sbin',
            '/usr/bin', '/sbin', '/bin'],
  }

  #Create a pinning
  $vcenter_compute_pkgs = [
    'python-bitstring', 'python-novaclient',
    'tzdata', 'tzdata-java', 'openjdk-7-jre-headless']

  apt::pin { 'vcenter_compute_pkgs_pin':
    explanation => 'Set override for packages from contrail repository',
    priority    => 1400,
    label       => 'contrail',
    packages    => $vcenter_compute_pkgs,
  } ->
  group { 'libvirtd':
    ensure => 'present',
  } ->
  package { $vcenter_compute_pkgs: } ->

  package { ['nova-compute', 'nova-compute-kvm', 'nova-common', 'python-nova']: } ->

  if $contrail::patch_nova_vmware {
    file { "${patch_path}/nova-vmware.patch":
      ensure => present,
      mode   => '0644',
      source => 'puppet:///modules/contrail/nova-vmware.patch',
    }->
    exec { 'patch-nova-vmware':
      command => 'patch -p1 < nova-vmware.patch',
      onlyif  => 'patch --dry-run -p1 < nova-vmware.patch',
      cwd     => $patch_path,
      require => Package['python-nova'],
    }
  }
  # Install vCenter-specific contrail packages
  package { ['libxml-commons-external-java', 'libxml-commons-resolver1.1-java',
    'libxerces2-java', 'libslf4j-java', 'libnetty-java', 'libjline-java',
    'libzookeeper-java']: } ->
  package { 'contrail-install-vcenter-plugin': } ->
  package { ['libcontrail-java-api', 'libcontrail-vijava',
    'libcontrail-vrouter-java-api']: } ->
  package { 'contrail-vcenter-plugin': }
}
