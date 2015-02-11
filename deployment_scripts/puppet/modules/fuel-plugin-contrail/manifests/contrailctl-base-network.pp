class contrailctl-base-network
{
  $contrail_settings = hiera("contrail")
  $network_scheme = hiera("network_scheme")

  prepare_network_config($network_scheme)
  $ifname=get_network_role_property('private','interface')

  $range_first=$contrail_settings['contrail_ip_start']
  $range_last=$contrail_settings['contrail_ip_end']
  $cidr=$contrail_settings['contrail_ip_netmask']
  $uid = hiera("uid")
  $node_ip=get_ip_from_range($range_first,$range_last,$cidr,$uid)

l23network::l3::ifconfig {"$ifname":
  interface => "$ifname",
  ipaddr => "$node_ip/$cidr"
}


}

class {"contrailctl-base-network":}
