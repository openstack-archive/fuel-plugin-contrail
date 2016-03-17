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

$common_pkg  = ['iproute2', 'haproxy', 'libatm1', 'libxen-4.4']
$libvirt_pkg = ['libvirt-bin', 'libvirt0']
$qemu_pkg    = ['qemu','qemu-*']

$keep_config_files = '-o Dpkg::Options::="--force-confold"'
$force_overwrite   = '-o Dpkg::Options::="--force-overwrite"'
$path_cmd    = ['/usr/local/sbin', '/usr/local/bin', '/usr/sbin', '/usr/bin', '/sbin', '/bin']
$patch_path  = '/usr/lib/python2.7/dist-packages'

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
  file {'/opt/contrail/contrail_install_repo_dpdk/Release':
    ensure  => file,
    content => 'Label: dpdk-depends-packages',
  } ->
  exec {'setup_dpdk_repo':
    command => 'bash /opt/contrail/contrail_packages_dpdk/setup.sh && touch /opt/contrail/dpdk-repo-DONE',
    path    => $path_cmd,
    creates => '/opt/contrail/dpdk-repo-DONE',
  }

  # Patch nova packages if it set on Fuel UI
  if $contrail::patch_nova {
    apt::pin { 'contrail-pin-nova':
      explanation => 'Prevent patched python-nova from upgrades',
      priority    => 1200,
      label       => '1:2015.1.1-1~u14.04+mos19665',
      packages    => 'python-nova',
    } ->
    file { "${patch_path}/nova-dpdk-vrouter.patch":
      ensure  => present,
      mode    => '0644',
      source  => 'puppet:///modules/contrail/nova-dpdk-vrouter.patch',
    }->
    exec { 'patch-python-nova':
      command => 'patch -p1 < nova-dpdk-vrouter.patch && touch python-nova-patch-DONE',
      path    => $path_cmd,
      cwd     => $patch_path,
      creates => "${patch_path}/python-nova-patch-DONE",
    }
  }

  # Override libvirt and qemu packages if it set on Fuel UI
  if $contrail::install_contrail_qemu_lv {
    # For qemu you don't need additional pinning, only dpdk repository
    apt::pin { 'contrail-pin-qemu':
      explanation => 'Install qemu from dpdk-depends',
      priority    => 1200,
      label       => 'dpdk-depends-packages',
      packages    => $qemu_pkg,
    } ->
    package { ['qemu-kvm','qemu-system-x86','qemu-systen-common']:
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
      label       => 'dpdk-depends-packages',
    } ->
# Install options are supported starting from puppet 3.5.1
#    package { $libvirt_pkg:
#      ensure          => '2:1.2.12-0ubuntu7+contrail2',
#      install_options => [$keep_config_files, $force_overwrite],
#    } ->
    exec { 'override-libvirt':
      command => "apt-get install --yes ${keep_config_files} ${force_overwrite} libvirt-bin libvirt0",
      path    => $path_cmd,
      unless  => 'dpkg -l | grep libvirt0 | grep contrail',
    } ->
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
    service { $contrail::libvirt_name:
      ensure => running,
      enable => true,
    } ~>
    service { 'nova-compute':
      ensure => running,
      enable => true,
    }
  }
}
