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
  # This class is kept here to ensure hugetlbfs mount existence,
  # even if user has missed nova hugepages configuration in UI/API.
  $node_hash       = hiera_hash('node', {})
  $nova_huge_pages = pick($node_hash['nova_hugepages_enabled'], false)

  if $contrail::compute_dpdk_enabled and !$nova_huge_pages and ($::osfamily == 'Debian') {
    $qemu_hugepages_value    = 'set KVM_HUGEPAGES 1'
    $libvirt_hugetlbfs_mount = 'set hugetlbfs_mount /run/hugepages/kvm'
    augeas { 'qemu_hugepages':
      context => '/files/etc/default/qemu-kvm',
      changes => $qemu_hugepages_value,
      notify  => Service[$contrail::libvirt_name],
    }
    augeas { 'libvirt_hugetlbfs_mount':
      context => '/files/etc/libvirt/qemu.conf',
      changes => $libvirt_hugetlbfs_mount,
      notify  => Service[$contrail::libvirt_name],
    }
    service { 'qemu-kvm':
      ensure => running,
      enable => true,
    }
    service { $contrail::libvirt_name:
      ensure => running,
      enable => true,
    }

    kernel_parameter { 'transparent_hugepage':
      ensure => present,
      value  => 'never',
    }

    Augeas['qemu_hugepages'] ~> Service<| title == 'qemu-kvm'|>
    Service<| title == 'qemu-kvm'|> -> Service<| title == $contrail::libvirt_name |>
  }
}
