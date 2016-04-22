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

notice('MODULAR: contrail/contrail-compute-vmware-repo.pp')

apt::pin { 'favor_contrail_packages':
  priority => 1400,
  label    => 'contrail',
}

# Temporary dirty hack. Fix execution of core manifests compute.pp and compute-vmware.pp.
# When contrail packages was installed, instead of libvirtd we will have libvirtd-bin files [FIXME]
file { '/etc/default/libvirtd':
  ensure  => present,
  content => '',
}

file { '/etc/init.d/libvirtd':
  ensure  => present,
  mode    => '0755',
  content => '',
}

exec { 'patch_core_vmware_manifest1':
  path    => '/usr/local/bin:/bin:/usr/bin/',
  cwd     => '/etc/puppet/modules/vmware/manifests',
  command => 'sed -i -e \'/\x27python-oslo.vmware\x27:/,+2d\' compute_vmware.pp',
}

exec { 'patch_core_vmware_manifest2':
  path    => '/usr/local/bin:/bin:/usr/bin/',
  cwd     => '/etc/puppet/modules/vmware/manifests',
  command => 'sed -i \'/Package\[\x27python-oslo.vmware\x27\]/d\' compute_vmware.pp',
}
