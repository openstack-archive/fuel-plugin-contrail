#    Copyright 2015 Mirantis, Inc.
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

class contrail::compute::hiera {

  # prevent to install and run open vSwitch on compute nodes
  # add packages overrides for libvirt and qemu.
  file { '/etc/hiera/plugins/contrail.yaml':
    ensure  => file,
    content => template('contrail/contrail_hiera.yaml.erb'),
  }
  if roles_include('dpdk') {
    file_line {'100-contrail-vrouter-override_ns':
        path  => '/etc/hiera.yaml',
        line  => '    - plugins/100-contrail-vrouter-override_ns',
        after => '  !ruby/sym hierarchy:',
    }
  }
}
