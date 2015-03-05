class contrail::network (
  $node_role,
  $address,
  $ifname = undef,
  $netmask,
  $public_addr = undef,
  $public_netmask = undef,
  $public_if = uned
  ) {

  case $node_role {
    'base-os':{
      # Remove interface from the bridge
      exec {"remove_${ifname}":
        command => "/sbin/brctl delif br-aux ${ifname}",
        returns => [0,1] # Idempotent
      }
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

   }
    'compute':{
      file {"/etc/network/interfaces.d/ifcfg-vhost0":
        ensure => present,
        content => template("contrail/ifcfg-vhost0.erb");
      }
    }
  }

}

