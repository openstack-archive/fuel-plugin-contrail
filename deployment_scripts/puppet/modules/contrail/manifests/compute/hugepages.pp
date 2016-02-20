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

  service { 'libvirtd':
    ensure    => running,
    enable    => true,
    subscribe => File['/etc/default/qemu-kvm'],
  }

  $hugepages_number = floor($::memorysize_mb * ${contrail::hugepages_amount} / '100' / ${contrail::hugepages_size})

  if dpdk_enabled {
    # NOTE: To use hugepages we have to upgrade qemu packages to version 2.4
    # The kernel configuration for hugepages
    Kernel_parameter {
      provider => 'grub2',
    }

    kernel_parameter { 'hugepagesz':
      ensure  => present,
      value   => ["${contrail::hugepages_size}M"],
    } ->
    kernel_parameter { 'hugepages':
      ensure  => present,
      value   => [$hugepages_number],
    }

    file { '/etc/default/qemu-kvm':
      owner   => 'root',
      group   => 'root',
      mode    => '0644',
      content => 'KVM_HUGEPAGES=1',
      notify  => Service['libvirtd'],
    }
  }
}
