class contrail::network (
  $node_role,
  $address,
  $ifname = undef,
  $netmask,
  $public_addr = undef,
  $public_netmask = undef,
  $public_if = undef,
  $public_gw = undef
  ) {

  Exec {
    path => '/bin:/sbin:/usr/bin:/usr/sbin',
  }

  # Remove interface from the bridge
  exec {"remove_${ifname}":
    command => "brctl delif br-aux ${ifname}",
    returns => [0,1] # Idempotent
  } ->
  file { '/etc/network/interfaces.d/ifcfg-br-aux':
    ensure => absent,
  } ->

  case $node_role {
    'base-os':{
      l23network::l3::ifconfig {$ifname:
        interface => $ifname,
        ipaddr    => "${address}/${netmask}",
      }
      # Contrail controller needs public ip anyway
      $public_ip_settings=hiera('public_network_assignment')
      $assign_public=$public_ip_settings['assign_to_all_nodes']
      if (! $assign_public) {
        l23network::l3::ifconfig {$public_if:
          interface => $public_if,
          ipaddr    => "${public_addr}/${public_netmask}",
        }
      }
      # l23network::l3::ifconfig does not brings the interface up. Bug? Check it later
      exec {"ifup-${public_if}":
        command => "ip link set up dev ${public_if}",
      } ->
      exec {'remove_default_gw':
          command => '/sbin/ip route del default',
          returns => [0,1] # Idempotent
      } ->
      # contrail controllers must be available from outer nets
      exec {"add-default-route-via-${public_gw}":
        command => "ip route add default via ${public_gw}",
      }
    }
    'compute':{
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

