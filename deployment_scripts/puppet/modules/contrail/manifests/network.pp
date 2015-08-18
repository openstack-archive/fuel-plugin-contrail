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
  $br_file = $operatingsystem ? {
      'Ubuntu' => '/etc/network/interfaces.d/ifcfg-br-mesh',
      'CentOS' => '/etc/sysconfig/network-scripts/ifcfg-br-mesh',
  }
  $gateways = split($contrail::settings['contrail_gateways'], ',')

  define contrail::network::add_route ( $destination, $gateway ) {
    exec {"check_route_to_${name}":
      command => "ip route del ${name}",
      onlyif  => "ip route | grep ${name}",
      before  => L23network::L3::Route[$name],
    }
    l23network::l3::route {$name:
      destination => $name,
      gateway     => $gateway,
    }
  }

  case $node_role {
    'base-os':{
      class { 'l23network': use_ovs => false }
      case $contrail::private_gw {
        '': { notify { 'No gateway for private network':} }
        default: {
          contrail::network::add_route { $gateways:
            destination => $gateways,
            gateway     => $contrail::private_gw,
          }
        }
      }
    }
    'compute':{
      file { $br_file: ensure => absent } ->
      # Remove interface from the bridge
      exec {"remove_${ifname}_mesh":
        command => "brctl delif br-mesh ${ifname}",
        returns => [0,1] # Idempotent
      } ->
      exec {'flush_addr_br_mesh':
        command => 'ip addr flush dev br-mesh',
        returns => [0,1] # Idempotent
      }
      case $operatingsystem {
        'Ubuntu': {
          file {'/etc/network/interfaces.d/ifcfg-vhost0':
            ensure  => present,
            content => template('contrail/ubuntu-ifcfg-vhost0.erb'),
          }
        }
        'CentOS': {
          exec {"remove_bridge_from_${ifname}_config":
            command => "sed -i '/BRIDGE/d' /etc/sysconfig/network-scripts/ifcfg-${ifname}",
          }
          file {'/etc/sysconfig/network-scripts/ifcfg-vhost0':
            ensure  => present,
            content => template('contrail/centos-ifcfg-vhost0.erb'),
          }
        default: {}
        }
      }
    }
    default: { notify { "Node role ${node_role} not supported": } }
  }

}

