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

notice('MODULAR: contrail/contrail-compute-repo.pp')

include contrail

apt::pin { 'contrail-main':
  explanation => 'Set priority for common contrail packages',
  priority    => 200,
  label       => 'contrail',
}

# Temporary dirty hack. In case when we use contrail dpdk repositorise
# we don't have nova-compute-kvm package there [FIXME]
exec { 'remove_nova_compute_kvm_dependency':
  path    => '/usr/local/bin:/bin:/usr/bin/',
  cwd     => '/etc/puppet/modules/nova/manifests/compute/',
  command => 'sed -i "/nova-compute-.{libvirt_virt_type}/,+5d" libvirt.pp',
}
