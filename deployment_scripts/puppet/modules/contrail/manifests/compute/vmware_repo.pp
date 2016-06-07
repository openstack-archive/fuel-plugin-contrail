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

class contrail::compute::vmware_repo {

  # NOTE(ak858f) This need to install qemu-kvm and qemu-system-x86
  if roles_include('compute-vmware') {
    include  ::contrail::compute::compute_repo
  }
  # NOTE(ak858f) This is only for contrail plugin repository
  apt::pin { 'contrail':
    priority   => 1400,
    label      => 'contrail',
    originator => 'contrail',
  }
  apt::pin { 'fixup_fox_libnl':
    explanation => 'Fix for libnl from contrail repo',
    packages    => 'libnl-route-3-200',
    priority    => '1500',
    originator  => 'infra-mirror-9.0-master trusty',
  }

  # [FIXME] Temporary dirty hack. Fix execution of core manifests compute.pp and
  # compute-vmware.pp. When contrail packages was installed, instead of libvirtd
  # we will have libvirt-bin files.

  file { '/etc/default/libvirtd':
    ensure  => present,
    content => '',
  }

  file { '/etc/init.d/libvirtd':
    ensure  => present,
    mode    => '0755',
    content => '',
  }

  file { '/opt/contrail':
    ensure  => directory,
  }

  file { '/etc/puppet/modules/vmware/templates/nova-compute.conf.erb':
    source => 'puppet:///modules/contrail/nova-compute.conf.erb_fixed',
  }

}
