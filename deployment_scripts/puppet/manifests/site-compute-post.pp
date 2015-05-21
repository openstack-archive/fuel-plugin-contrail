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

include contrail
$node_role = 'compute'
Exec { path => '/bin:/sbin:/usr/bin:/usr/sbin', refresh => 'echo NOOP_ON_REFRESH'}

class { 'contrail::network':
  node_role => $node_role,
  address   => $contrail::address,
  ifname    => $contrail::ifname,
  netmask   => $contrail::netmask_short,
} ->

case $operatingsystem {
  Ubuntu: {

    class { 'contrail::package':
      install => ['contrail-openstack-vrouter','contrail-vrouter-dkms','iproute2','haproxy','libatm1'],
      remove  => ['openvswitch-common','openvswitch-datapath-dkms','openvswitch-datapath-lts-saucy-dkms','openvswitch-switch','nova-network','nova-api'],
      }

  }
  CentOS: {
    class { 'contrail::package':
      install => ['contrail-openstack-vrouter','iproute','haproxy','patch'],
      remove  => ['openvswitch','openstack-neutron-openvswitch','kmod-openvswitch-lt'],
    }
    ->
    class { 'contrail::vrouter_module':}
    ->
    file { '/etc/supervisord.conf':
      ensure => 'link',
      target => '/etc/contrail/supervisord_vrouter.conf',
      force  => 'yes',
    }
    ->
    file {'/etc/contrail/default_pmac':
              ensure => present,
    }
    ->
    service {'supervisor-vrouter': enable => true}
  }
} ->

class { 'contrail::config':
  node_role => $node_role,
} ->

class { 'contrail::provision':
  node_role => $node_role,
}
