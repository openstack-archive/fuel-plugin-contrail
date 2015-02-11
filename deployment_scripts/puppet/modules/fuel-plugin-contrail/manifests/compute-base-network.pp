class compute-base-network 
{
  $contrail_settings = hiera("contrail")

  $range_first=$contrail_settings['contrail_ip_start']
  $range_last=$contrail_settings['contrail_ip_end']
  $cidr=$contrail_settings['contrail_ip_netmask']
  $uid = hiera("uid")

  $node_ip=get_ip_from_range($range_first,$range_last,$cidr,$uid)
  $node_netmask=cidr_to_netmask($cidr)

  file {"/etc/network/interfaces.d/ifcfg-vhost0":
         ensure => present,
         content => template("fuel-plugin-contrail/ifcfg-vhost0.erb");
       }

}
