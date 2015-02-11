class contrail::contrailctl-base-network
{
  $contrail_settings = hiera("contrail")
  $network_scheme = hiera("network_scheme")

  prepare_network_config($network_scheme)
  $ifname=get_network_role_property('private','interface')

  $range_first=$contrail_settings['contrail_private_start']
  $range_last=$contrail_settings['contrail_private_end']
  $cidr=$contrail_settings['contrail_private_cidr']
  $uid = hiera("uid")
  $node_ip=get_ip_from_range($range_first,$range_last,$cidr,$uid)

  l23network::l3::ifconfig {"$ifname":
    interface => "$ifname",
    ipaddr => "$node_ip/$cidr"
  }


  package { "keepalived": 
    ensure => "installed",
          }
  ->
  file {"/etc/keepalived/keepalived.conf":
         ensure => present,
         content => template("contrail/keepalived.conf.erb"),
       }
  ->
  service {"keepalived":
         ensure => running,
       }

}
