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

class contrail::compute::sriov {

  if $contrail::compute_sriov_enabled {
    # NOTE: To use hugepages we have to upgrade qemu packages to version 2.4
    # The kernel configuration for hugepages
    Kernel_parameter {
      provider => 'grub2',
    }

    kernel_parameter { 'nomdmonddf':
      ensure => present,
    }
    kernel_parameter { 'nomdmonisw':
      ensure => present,
    }
    kernel_parameter { 'intel_iommu':
      ensure => present,
      value  => "on",
    }

    file_line {'sriov':
      line      => "echo ${sriov_device_no} > /sys/class/net/${sriov_device}/device/sriov_numvfs",
      path      => '/etc/rc.local',
      match    => '^exit'
    }

    exec { 'reboot_require':
      path    => ['/bin', '/usr/bin'],
      command => 'touch /tmp/contrail-reboot-require'
    }
  }
}
