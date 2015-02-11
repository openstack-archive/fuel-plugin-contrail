# General configuration
$settings = hiera('contrail')
$network_scheme = hiera("network_scheme")
$uid = hiera("uid")

# Network configuration
prepare_network_config($network_scheme)
$ifname = get_network_role_property('private','interface')
$range_first = $settings['contrail_private_start']
$range_last = $settings['contrail_private_end']
$cidr = $settings['contrail_private_cidr']
$node_ip=get_ip_from_range($range_first,$range_last,$cidr,$uid)

class { 'contrail::network':
  node_role   => 'compute',
  node_ip     => $node_ip,
  ifname      => $ifname,
  cidr        => $cidr,
}
