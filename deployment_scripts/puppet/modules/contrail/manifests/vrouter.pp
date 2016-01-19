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

class contrail::vrouter {

  class { 'contrail::package':
    install => ['contrail-openstack-vrouter','contrail-vrouter-dkms','iproute2','haproxy','libatm1'],
    remove  => ['openvswitch-common','openvswitch-datapath-dkms','openvswitch-datapath-lts-saucy-dkms','openvswitch-switch','nova-network','nova-api'],
  } ->
  exec { 'remove-ovs-modules':
    command => '/sbin/modprobe -r openvswitch'
  }

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

  file {'/etc/init.d/fixup-vrouter':
    ensure => present,
    mode   => '0755',
    owner  => 'root',
    group  => 'root',
    source => 'puppet:///modules/contrail/fixup-vrouter.init',
  } ->

  service {'fixup-vrouter':
    ensure => running,
    enable => true,
  } ->
  service {'supervisor-vrouter':
    ensure    => running,
    enable    => true,
    subscribe => [Package['contrail-openstack-vrouter','contrail-vrouter-dkms'],
                  File['/etc/contrail/agent_param','/etc/contrail/contrail-vrouter-agent.conf',
                  '/etc/contrail/contrail-vrouter-nodemgr.conf']
                  ],
  }
}
