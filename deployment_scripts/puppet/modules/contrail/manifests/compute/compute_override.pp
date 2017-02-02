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

class contrail::compute::compute_override {

  $common_pkg  = ['iproute2', 'haproxy', 'libatm1', 'libxen-4.4']
  $libvirt_pkg = ['libvirt-bin', 'libvirt0']
  $qemu_pkg    = ['qemu','qemu-*']

  $keep_config_files = '-o Dpkg::Options::="--force-confold"'
  $force_overwrite   = '-o Dpkg::Options::="--force-overwrite"'
  $allow_unsigned    = '-o APT::Get::AllowUnauthenticated=1'
  $patch_path  = '/usr/lib/python2.7/dist-packages'

  Exec {
    path => ['/usr/local/sbin', '/usr/local/bin', '/usr/sbin', '/usr/bin', '/sbin', '/bin'],
  }

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
    exec { 'update-dpdk-repo':
      command => 'dpkg-scanpackages . /dev/null | gzip -9c > Packages.gz',
      cwd     => '/opt/contrail/contrail_install_repo_dpdk',
    } ->
    file {'/opt/contrail/contrail_install_repo_dpdk/Release':
      ensure  => file,
      content => 'Label: dpdk-depends-packages',
    } ->
    apt::source { 'dpdk-depends-repo':
      location    => 'file:/opt/contrail/contrail_install_repo_dpdk',
      repos       => './',
      release     => ' ',
      include_src => false,
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
        ensure => present,
        mode   => '0644',
        source => 'puppet:///modules/contrail/nova-dpdk-vrouter.patch',
      }->
      exec { 'patch-python-nova':
        command => 'patch -p1 < nova-dpdk-vrouter.patch && touch python-nova-patch-DONE',
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
      exec {'override-qemu':
        command => "apt-get install --yes ${keep_config_files} ${force_overwrite} ${allow_unsigned} \
qemu-kvm qemu-system-x86 qemu-system-common",
        unless  => 'dpkg -l | grep qemu-system-common | grep contrail',
        require => Apt::Source['dpdk-depends-repo'],
      }
      if !defined(Service['qemu-kvm']) {
        service { 'qemu-kvm':
          ensure  => running,
          enable  => true,
          require => Exec['override-qemu'],
        }
      }
      apt::pin { 'contrail-override-libvirt':
        explanation => 'Set priority for packages that need to override from contrail repository',
        packages    => $libvirt_pkg,
        priority    => 1200,
        label       => 'dpdk-depends-packages',
        require     => Service['qemu-kvm'],
      } ->
      # Install options are supported starting from puppet 3.5.1
      #package { $libvirt_pkg:
      #  ensure          => '2:1.2.12-0ubuntu7+contrail2',
      #  install_options => [$keep_config_files, $force_overwrite],
      #} ->
      exec { 'override-libvirt':
        command => "apt-get install --yes ${keep_config_files} ${force_overwrite} ${allow_unsigned} libvirt-bin libvirt0",
        unless  => 'dpkg -l | grep libvirt0 | grep contrail',
        require => Apt::Source['dpdk-depends-repo'],
      }
      # With a new libvirt packages this init script must be stopped
      if !defined(Service['libvirtd']) {
        service { 'libvirtd':
          ensure  => stopped,
          enable  => false,
          require => Exec['override-libvirt'],
        }
      }
      else {
        Service <| (title == 'libvirtd') |> {
          ensure => stopped,
          enable => false,
        }
      }
      # This options must be uncommented for correct work with nova-compute
      file_line { 'add_libvirt_opt1':
        path    => '/etc/libvirt/libvirtd.conf',
        match   => 'auth_unix_ro',
        line    => 'auth_unix_ro = "none"',
        require => Service['libvirtd'],
      } ->
      file_line { 'add_libvirt_opt2':
        path  => '/etc/libvirt/libvirtd.conf',
        match => 'auth_unix_rw',
        line  => 'auth_unix_rw = "none"',
      } ~>
      service { $contrail::libvirt_name:
        ensure => running,
        enable => true,
      }
      if !defined(Service['nova-compute']) {
        service { 'nova-compute':
          ensure  => running,
          enable  => true,
          require => Service[$contrail::libvirt_name],
        }
      }
    }
  }
}
