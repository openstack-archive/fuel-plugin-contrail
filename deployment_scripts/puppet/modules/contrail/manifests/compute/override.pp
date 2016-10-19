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

class contrail::compute::override {


  $common_pkg  = ['iproute2', 'haproxy', 'libatm1', 'libxen-4.4']
  $libvirt_pkg = ['libvirt-bin', 'libvirt0']
  $qemu_pkg    = ['qemu','qemu-*']
  $nova_pkg    = ['nova-compute', 'nova-common', 'python-nova', 'python-urllib3', 'nova-compute-libvirt', 'nova-compute-kvm']

  $keep_config_files = '-o Dpkg::Options::="--force-confold"'
  $force_overwrite   = '-o Dpkg::Options::="--force-overwrite"'
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
    apt::conf { 'allow-unathenticated':
      content => 'APT::Get::AllowUnauthenticated 1;',
    } ->
    apt::source { 'dpdk-depends-repo':
      location    => 'file:/opt/contrail/contrail_install_repo_dpdk',
      repos       => './',
      release     => ' ',
    }
    # Patch nova packages if it set on Fuel UI
    if $contrail::patch_nova {
      apt::pin { 'contrail-override-nova':
        explanation => 'Set priority for packages that need to override from contrail repository',
        priority    => 1200,
        label       => 'contrail',
        packages    => $nova_pkg,
      } ->
      #TODO rewrite using package
      exec { 'override-nova':
        command => "apt-get install --yes --force-yes ${keep_config_files} ${force_overwrite} nova-compute nova-compute-kvm",
        unless  => 'dpkg -l | grep nova-compute | grep contrail',
        require => Apt::Conf['allow-unathenticated'],
      }
    }

    if $contrail::install_contrail_qemu_lv {
      # For qemu you don't need additional pinning, only dpdk repository
      apt::pin { 'contrail-pin-qemu':
        explanation => 'Install qemu from dpdk-depends',
        priority    => 1200,
        label       => 'dpdk-depends-packages',
        packages    => $qemu_pkg,
      } ->
      exec {'override-qemu':
        command => "apt-get install --yes ${keep_config_files} ${force_overwrite} \
        qemu-kvm qemu-system-x86 qemu-system-common",
        unless  => 'dpkg -l | grep qemu-system-common | grep contrail',
        require => Apt::Source['dpdk-depends-repo'],
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
        command => "apt-get remove --yes --force-yes ${keep_config_files} ${force_overwrite} libvirt-daemon-system",
        unless  => 'dpkg -l | grep libvirt0 | grep contrail',
        require => Apt::Source['dpdk-depends-repo'],
      } ->
      exec { 'install-nova':
        command => "apt-get install --yes --force-yes ${keep_config_files} ${force_overwrite} nova-compute nova-compute-kvm",
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
}
