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

class contrail::compute::hugepages {

  if $contrail::dpdk_enabled {
    # NOTE: To use hugepages we have to upgrade qemu packages to version 2.4
    # The kernel configuration for hugepages
    Kernel_parameter {
      provider => 'grub2',
    }

    if $contrail::hugepages_size == 2 {
      sysctl::value { 'vm.nr_hugepages':
        value => "${contrail::hugepages_number} ",
      }

      kernel_parameter { 'hugepagesz':
        ensure => absent,
      }

      kernel_parameter { 'hugepages':
        ensure => absent,
      }
    }
    elsif $contrail::hugepages_size == 1024 {
      kernel_parameter { 'hugepagesz':
        ensure => present,
        value  => "${contrail::hugepages_size}M",
      } ->

      kernel_parameter { 'hugepages':
        ensure => present,
        value  => $contrail::hugepages_size,
      }

      exec { 'reboot_require':
        path    => ['/bin', '/usr/bin'],
        command => 'touch /tmp/contrail-reboot-require',
        onlyif  => 'test ! -d /sys/kernel/mm/hugepages/hugepages-1048576kB',
      }
    }

    file { '/etc/default/qemu-kvm':
      owner   => 'root',
      group   => 'root',
      mode    => '0644',
      content => 'KVM_HUGEPAGES=1',
      notify  => Service['libvirtd'],
    }

    service { 'libvirtd':
      ensure    => running,
      enable    => true,
      subscribe => File['/etc/default/qemu-kvm'],
    }
  }
}
