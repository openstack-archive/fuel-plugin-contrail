class contrail::network (
  $node_role,
  $address,
  $ifname = undef,
  $netmask,
  ) {

  case $node_role {
    'base-os':{
      # Remove interface from the bridge
      exec {"remove_${ifname}":
        command => "/sbin/brctl delif br-aux ${ifname}"
      }
      l23network::l3::ifconfig {$ifname:
        interface => $ifname,
        ipaddr    => "${address}/${netmask}",
      }
   }
    'compute':{
      file {"/etc/network/interfaces.d/ifcfg-vhost0":
        ensure => present,
        content => template("contrail/ifcfg-vhost0.erb");
      }
      # Remove interface from the bridge
      exec {"remove_${ifname}":
        command => "/sbin/brctl delif br-aux ${ifname}"
      }
    }
  }

}

