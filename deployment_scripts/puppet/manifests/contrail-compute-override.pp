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

notice('MODULAR: contrail/contrail-compute-override.pp')

include contrail

$common_pkg  = ['iproute2', 'haproxy', 'libatm1']
$nova_pkg    = ['nova-compute', 'nova-common', 'python-nova', 'python-urllib3']
$libvirt_pkg = ['libvirt-bin', 'libvirt0']

$install_cmd = 'apt-get install --yes -o Dpkg::Options::="--force-overwrite" -o Dpkg::Options::="--force-confold"'
$path_cmd    = ['/usr/local/sbin', '/usr/local/bin', '/usr/sbin', '/usr/bin', '/sbin', '/bin']

apt::pin { 'contrail-override-common':
  explanation => 'Set priority for packages that need to override from contrail repository',
  priority    => 1200,
  label       => 'contrail',
  packages    => $common_pkg,
}

if $contrail::compute_dpdk_enabled {
  # Create local dpdk repository
  package { 'dpdk-depends-packages':
    ensure => present,
  } ->
  exec {'setup_dpdk_repo':
    command => 'bash /opt/contrail/contrail_packages_dpdk/setup.sh',
    path => $path_cmd,
  }

  # Override nova packages if it set on Fuel UI
  if $contrail::install_contrail_nova {
    apt::pin { 'contrail-override-nova':
      explanation => 'Set priority for packages that need to override from contrail repository',
      priority    => 1200,
      label       => 'contrail',
      packages    => $nova_pkg,
    } ->
    #TODO rewrite using package
    exec { 'override-nova':
      command => "${install_cmd} nova-compute",
      path => $path_cmd,
    }
  }

  # Override libvirt and qemu packages if it set on Fuel UI
  if $contrail::install_contrail_qemu_lv {
    # For qemu you don't need additional pinning, only dpdk repository
    package { 'qemu-system-x86':
      ensure => 'latest',
    } ~>
    service { 'qemu-kvm':
      ensure => running,
      enable => true,
    } ->
    apt::pin { 'contrail-override-libvirt':
      explanation => 'Set priority for packages that need to override from contrail repository',
      packages    => $libvirt_pkg,
      priority    => 1200,
      version     => '2:1.2.12-0ubuntu7+contrail2',
    } ->
    #TODO rewrite using package
    exec { 'override-libvirt':
      command => "${install_cmd} libvirt-bin libvirt0",
      path => $path_cmd,
    } ~>
    # With a new libvirt packages this init script must be stopped
    service { 'libvirtd':
      ensure => stopped,
      enable => false,
    } ->
    # This options must be uncommented for correct work with nova-compute
    file_line { 'add_libvirt_opt1':
      path  => '/etc/libvirt/libvirtd.conf',
      match => 'auth_unix_ro',
      line  => 'auth_unix_ro = "none"',
    } ->
    file_line { 'add_libvirt_opt2':
      path  => '/etc/libvirt/libvirtd.conf',
      match => 'auth_unix_rw',
      line  => 'auth_unix_rw = "none"',
    } ~>
    service { 'libvirt-bin':
      ensure => running,
      enable => true,
    } ~>
    service { 'nova-compute':
      ensure => running,
      enable => true,
    }
  }
}

