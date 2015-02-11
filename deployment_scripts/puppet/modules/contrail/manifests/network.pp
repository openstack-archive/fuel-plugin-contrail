class contrail::network (
  $node_role,
  $address,
  $ifname = undef,
  $netmask,
  ) {

  case $node_role {
    'base-os':{
      l23network::l3::ifconfig {$ifname:
        interface => $ifname,
        ipaddr    => "${address}/${netmask}",
      }
      ->
      # l23network::l3::ifconfig does not brings the interface up. Bug? Check it later
      exec {"ifup-${ifname}":
        command => "/sbin/ip link set up dev $ifname"
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

