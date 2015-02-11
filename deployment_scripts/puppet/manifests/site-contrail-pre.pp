 $contrail_settings = hiera("contrail")
 $network_scheme = hiera("network_scheme")

 prepare_network_config($network_scheme)
 $ifname=get_network_role_property('private','interface')

 $range_first=$contrail_settings['contrail_private_start']
 $range_last=$contrail_settings['contrail_private_end']
 $cidr=$contrail_settings['contrail_private_cidr']
 $uid = hiera("uid")
 $node_ip=get_ip_from_range($range_first,$range_last,$cidr,$uid)
 $node_role = hiera('role')

class { contrail::packages:
  install => ['python-crypto','python-netaddr','python-paramiko',
  'contrail-fabric-utils','contrail-setup'],
  responsefile => 'contrail.preseed',
}

class { 'contrail::network':
  node_role => 'compute',
  range_first => $range_first,
  range_last => $range_last,
  cidr => $cidr,
  uid => $uid,
}
