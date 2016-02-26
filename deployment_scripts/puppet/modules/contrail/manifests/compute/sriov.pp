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

    Kernel_parameter {
      provider => 'grub2',
    }

    kernel_parameter { 'intel_iommu':
      ensure => present,
      value  => 'on',
    }

    kernel_parameter { 'iommu':
      ensure => present,
      value  => 'pt',
    }

    create_resources(contrail::rclocal_vfs, $::contrail::sriov_hash)

    file_line {"sriov ${title}":
      ensure => absent,
      path   => '/etc/rc.local',
      line   => 'exit 0'
    }

    exec { 'reboot_require':
      path    => ['/bin', '/usr/bin'],
      command => 'touch /tmp/contrail-reboot-require'
    }
  }
}
