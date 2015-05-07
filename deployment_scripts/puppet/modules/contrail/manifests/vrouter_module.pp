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

class contrail::vrouter_module () {
  package {['contrail-vrouter-source','dkms']:
    ensure => present,
    install_options => ['nogpgcheck'] # dkms package it not signed yet
  }
  ->

  file {'/tmp/vrouter.patch':
    ensure => file,
    source => 'puppet:///modules/contrail/vrouter.patch'
  }
  ->

  file {'/usr/src/vrouter-2.01': ensure => directory }
  ->

  exec {'unpack_src':
    command =>'tar -xf /usr/src/modules/contrail-vrouter/contrail-vrouter-2.01.tar.gz -C /usr/src/vrouter-2.01',
  }
  ->

  file {'/usr/src/vrouter-2.01/dkms.conf':
    ensure => file,
    source => 'puppet:///modules/contrail/dkms.conf'
  }
  ->

  exec {'patch_vrouter':
    command =>'patch /usr/src/vrouter-2.01/include/vr_compat.h /tmp/vrouter.patch',
  }
  ->

  exec {'build_install_module':
    command =>'dkms add vrouter/2.01 && dkms build vrouter/2.01 && dkms install vrouter/2.01',
  }
}
