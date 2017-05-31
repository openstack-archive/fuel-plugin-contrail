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

  $common_pkg        = ['iproute2', 'haproxy', 'libatm1', 'libxen-4.4']
  $libvirt_pkg       = ['libvirt-bin', 'libvirt0']
  $qemu_pkg          = ['qemu-kvm', 'qemu-system-x86', 'qemu-system-common']
  $patch_path        = '/usr/lib/python2.7/dist-packages'
  $install_options   = ['-o', 'Dpkg::Options::=', '--force-confold', '-o', 'Dpkg::Options::=', '--force-overwrite']

  Exec {
    path => ['/usr/local/sbin', '/usr/local/bin', '/usr/sbin', '/usr/bin', '/sbin', '/bin'],
  }

  apt::pin { 'contrail-override-common':
    explanation => 'Set priority for packages that need to override from contrail repository',
    priority    => 1200,
    label       => 'contrail',
    packages    => $common_pkg,
  }

    # Override libvirt and qemu packages if it set on Fuel UI
    if $contrail::install_contrail_qemu_lv {
      if $contrail::compute_dpdk_enabled {
        $pin_label = 'dpdk-depends-packages'

        package { 'dpdk-depends-packages':
          ensure => present,
        } ->
        exec { 'update-dpdk-repo':
          command => 'dpkg-scanpackages . /dev/null | gzip -9c > Packages.gz',
          cwd     => '/opt/contrail/contrail_install_repo_dpdk',
        } ->
        file {'/opt/contrail/contrail_install_repo_dpdk/Release':
          ensure  => file,
          content => "Label: ${pin_label}",
        } ->
        apt::source { 'dpdk-depends-repo':
          location    => 'file:/opt/contrail/contrail_install_repo_dpdk',
          repos       => './',
          release     => ' ',
          include_src => false,
          before      => Package['qemu-kvm', 'libvirt0', 'libvirt-bin']
        } ->
        apt::pin { 'contrail-pin-qemu':
          explanation => 'Install qemu from dpdk-depends',
          priority    => 1200,
          label       => $pin_label,
          packages    => ['qemu', 'qemu-*'],
          before      => Package[$qemu_pkg],
        }

      } else {
          $pin_label = 'contrail'
        }

      # For qemu you don't need additional pinning, only dpdk repository
      if !defined(Package['qemu-kvm']) {
        package{'qemu-kvm':
          ensure          => latest,
          provider        => apt,
          install_options => $install_options,
        }
      }
      if !defined(Package['qemu-system-x86']) {
        package{'qemu-system-x86':
          ensure          => latest,
          provider        => apt,
          install_options => $install_options,
        }
      }
      if !defined(Package['qemu-system-common']) {
        package{'qemu-system-common':
          ensure          => latest,
          provider        => apt,
          install_options => $install_options,
        }
      }
      if !defined(Service['qemu-kvm']) {
        service { 'qemu-kvm':
          ensure  => running,
          enable  => true,
          require => Package[$qemu_pkg],
        }
      }
      apt::pin { 'contrail-override-libvirt':
        explanation => 'Set priority for packages that need to override from contrail repository',
        packages    => $libvirt_pkg,
        priority    => 1200,
        label       => $pin_label,
        require     => Service['qemu-kvm'],
      }
      if !defined(Package['libvirt-bin']) {
        package{'libvirt-bin':
          ensure          => latest,
          provider        => apt,
          install_options => $install_options,
          require         => Apt::Pin['contrail-override-libvirt'],
        }
      }
      if !defined(Package['libvirt0']) {
        package{'libvirt0':
          ensure          => latest,
          provider        => apt,
          install_options => $install_options,
          require         => Apt::Pin['contrail-override-libvirt'],
        }
      }
      # With a new libvirt packages this init script must be stopped
      if !defined(Service['libvirtd']) {
        service { 'libvirtd':
          ensure  => stopped,
          enable  => false,
          require => Package[$libvirt_pkg],
        }
      }
      else {
        Service <| (title == 'libvirtd') |> {
          ensure => stopped,
          enable => false,
        }
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
      Service[$contrail::libvirt_name]

      if !defined(Service[$contrail::libvirt_name]) {
          service { $contrail::libvirt_name:
            ensure => running,
            enable => true,
          }
      }

      if !defined(Service['nova-compute']) {
        service { 'nova-compute':
          ensure  => running,
          enable  => true,
          require => Service[$contrail::libvirt_name],
        }
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
        onlyif  => 'patch --dry-run -p1 < nova-dpdk-vrouter.patch',
        cwd     => $patch_path,
        creates => "${patch_path}/python-nova-patch-DONE",
      }
    }
}

