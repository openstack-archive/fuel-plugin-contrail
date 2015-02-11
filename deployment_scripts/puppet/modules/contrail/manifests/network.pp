class contrail::network (
  $node_role,
  $node_ip,
  $ifname = undef,
  $cidr,
  ) {

  case $node_role {
    'base-os':{
      l23network::l3::ifconfig {$ifname:
        interface => $ifname,
        ipaddr => "${node_ip}/${cidr}"
      }
    }
    'compute':{
      $node_netmask=cidr_to_netmask($cidr)
      file {"/etc/network/interfaces.d/ifcfg-vhost0":
        ensure => present,
        content => template("contrail/ifcfg-vhost0.erb");
      }
    }
  }

}

