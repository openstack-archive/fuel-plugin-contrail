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

apt::pin { 'favor_contrail_packages':
  priority => 1400,
  label    => 'contrail',
}

apt::pin { 'fixup_fox_libnl':
  explanation => 'Fix for libnl from contrail repo',
  packages    => ['libnl-route-3-200', 'libnl-3-200'],
  priority    => '1500',
  label       => 'Ubuntu',
} ->

package {'libnl-3-200':
  ensure => '3.2.21-1ubuntu3',
}

file { '/etc/hiera/override/plugins.yaml':
  source => "puppet:///modules/contrail/vmware_data_${contrail::cluster_id}.yaml",
}

file { '/etc/hiera/plugins/contrail.yaml':
  ensure  => file,
  content => 'libvirt_type: kvm',
}

# Temporary dirty hack. Fix execution of core manifests compute.pp and compute-vmware.pp.
# When contrail packages was installed, instead of libvirtd we will have libvirt-bin files [FIXME]
file { '/etc/default/libvirtd':
  ensure  => present,
  content => '',
}

file { '/etc/init.d/libvirtd':
  ensure  => present,
  mode    => '0755',
  content => '',
}

exec { 'patch_core_vmware_manifest':
  path    => '/usr/local/bin:/bin:/usr/bin/',
  cwd     => '/etc/puppet/modules/openstack_tasks/manifests/roles/',
  command => 'sed -i -e \'s/$libvirt_type_kvm \+= \x27qemu-kvm\x27/$libvirt_type_kvm = \x27qemu-system-x86\x27/g\' compute.pp',
}

file { '/etc/puppet/modules/vmware/templates/nova-compute.conf.erb':
  source => 'puppet:///modules/contrail/nova-compute.conf.erb_fixed',
}

}
