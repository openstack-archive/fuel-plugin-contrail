class contrail::network ($node_role, $range_first, $range_last, $cidr, $uid)
{

  case $node_role {

    'base-os':{

      l23network::l3::ifconfig {"$ifname":
        interface => "$ifname",
        ipaddr => "$node_ip/$cidr"
      }

      package { "keepalived": ensure => "installed"}
      ->
      file {"/etc/keepalived/keepalived.conf":
             ensure => present,
             content => template("contrail/keepalived.conf.erb"),
           }
      ->
      service {"keepalived": ensure => running}
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

