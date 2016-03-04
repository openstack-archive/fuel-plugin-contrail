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

class contrail::compute::vrouter {
  if $contrail::compute_dpdk_enabled {
    $install_packages = ['contrail-openstack-vrouter','contrail-vrouter-dpdk-init','iproute2','haproxy','libatm1']
    $delete_packages  = ['openvswitch-common','openvswitch-datapath-dkms','openvswitch-datapath-lts-saucy-dkms','openvswitch-switch','nova-network','nova-api']
    file {'/etc/contrail/supervisord_vrouter_files/contrail-vrouter-dpdk.ini':
      ensure  => present,
      content => template('contrail/contrail-vrouter-dpdk.ini.erb'),
      require => Class[Contrail::Package],
      notify  => Service['supervisor-vrouter'],
    }
  } else {
    $install_packages = ['contrail-openstack-vrouter','contrail-vrouter-dkms','iproute2','haproxy','libatm1']
    $delete_packages  = ['openvswitch-common','openvswitch-datapath-dkms','openvswitch-datapath-lts-saucy-dkms','openvswitch-switch','nova-network','nova-api']
  }
  file { 'create_supervisor_vrouter_override':
    ensure  => present,
    path    => '/etc/init/supervisor-vrouter.override',
    content => 'manual',
  } ->
  class { 'contrail::package':
    install => [$install_packages],
    remove  => [$delete_packages],
  } ->
  exec { 'remove-ovs-modules':
    command => '/sbin/modprobe -r openvswitch'
  } ->
  file {'/etc/contrail/agent_param':
    ensure  => present,
    content => template('contrail/agent_param.erb'),
    require => Class[Contrail::Package],
  } ->
  file {'/etc/contrail/contrail-vrouter-agent.conf':
    ensure  => present,
    content => template('contrail/contrail-vrouter-agent.conf.erb'),
  } ->
  file {'/etc/contrail/contrail-vrouter-nodemgr.conf':
    ensure  => present,
    content => template('contrail/contrail-vrouter-nodemgr.conf.erb'),
  }
  exec { 'remove_supervisor_override':
    command  => 'rm -rf /etc/init/supervisor-vrouter.override',
    provider => shell,
  } ->
  service {'supervisor-vrouter':
    ensure    => running,
    enable    => true,
    subscribe => [Class[Contrail::Package],Exec['remove-ovs-modules'],
                  File['/etc/contrail/agent_param','/etc/contrail/contrail-vrouter-agent.conf',
                  '/etc/contrail/contrail-vrouter-nodemgr.conf']
                  ],
  }
}
