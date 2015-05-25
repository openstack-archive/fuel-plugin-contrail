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

class contrail::network (
  $node_role,
  $address,
  $ifname = undef,
  $netmask,
  $default_gw = undef
  ) {
  $br_aux_file = $operatingsystem ? {
      'Ubuntu' => '/etc/network/interfaces.d/ifcfg-br-aux',
      'CentOS' => ['/etc/sysconfig/network-scripts/ifcfg-br-aux',"/etc/sysconfig/network-scripts/ifcfg-${ifname}"],
  }

  # Remove interface from the bridge
  exec {"remove_${ifname}":
    command => "brctl delif br-aux ${ifname}",
    returns => [0,1] # Idempotent
  } ->
  file { $br_aux_file: ensure => absent }
  ->

  case $node_role {
    'base-os':{
      l23network::l3::ifconfig {$ifname:
        interface => $ifname,
        ipaddr    => "${address}/${netmask}",
      }
      exec {'remove_default_gw':
          command => '/sbin/ip route del default',
          returns => [0,2] # Idempotent
      } ->
      exec {"add-default-route-via-${default_gw}":
        command => "ip route add default via ${default_gw}",
      }
    }
    'compute':{
      file {'/etc/hiera/override/plugins.yaml':
        ensure => present,
        source => 'puppet:///modules/contrail/plugins.yaml',
      }
      case $operatingsystem
      {
          Ubuntu:
          {
            file {'/etc/network/interfaces.d/ifcfg-vhost0':
              ensure => present,
              content => template('contrail/ubuntu-ifcfg-vhost0.erb');
            }
          }

          CentOS:
          {
            file {'/etc/sysconfig/network-scripts/ifcfg-vhost0':
              ensure => present,
              content => template('contrail/centos-ifcfg-vhost0.erb');
            }
          }
      }
    }
    default: { notify { "Node role ${node_role} not supported": } }
  }

}

