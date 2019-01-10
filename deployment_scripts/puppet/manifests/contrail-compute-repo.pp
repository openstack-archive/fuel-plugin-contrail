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

if $contrail::compute_dpdk_enabled {
  $configure_default_route = '/etc/puppet/modules/osnailyfacter/modular/netconfig/configure_default_route.pp'
  $netconfig = '/etc/puppet/modules/osnailyfacter/modular/netconfig/netconfig.pp'

  exec {'no_default_route_reconfigure':
    command => "/bin/echo '#NOOP here. Modified by contrail plugin' > ${configure_default_route}",
  }

  exec {'no_netconfig':
    path    => '/usr/local/bin:/bin:/usr/bin/',
    command => "/bin/echo '#NOOP here. Modified by contrail plugin' > ${netconfig}",
    onlyif  => 'dpkg -l | grep contrail-vrouter-dpdk-init'
  }

  $nova_params = '/etc/puppet/modules/nova/manifests/params.pp'
  $libvirt_from_contrail = 'dpkg -l | grep libvirt0 | grep contrail'

  exec {'libvirt name fix':
    path    => '/usr/local/bin:/bin:/usr/bin/',
    command => "sed -i 's/libvirtd/libvirt-bin/g' ${nova_params}",
    onlyif  => $libvirt_from_contrail,
  }

}
