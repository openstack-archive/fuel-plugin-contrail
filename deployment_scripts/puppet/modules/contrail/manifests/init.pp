class contrail {

# General configuration
$settings = hiera('contrail')
$network_scheme = hiera("network_scheme")
$uid = hiera("uid")
$node_role = hiera('role')

# Network configuration
prepare_network_config($network_scheme)
$ifname = get_network_role_property('private','interface')
$range_first = $settings['contrail_private_start']
$range_last = $settings['contrail_private_end']
$cidr = $settings['contrail_private_cidr'] # "cidr" is actually a network address with subnet, i.e. 192.168.150.0/24
$netmask=cidr_to_netmask($cidr) # returns i.e. "255.255.255.0"
$netmask_short=netmask_to_cidr($cidr) # returns i.e. "/24"
$address=get_ip_from_range($range_first,$range_last,$netmask,$uid)


# Package configuration
$master_ip = hiera('master_ip')
$master_port = '8080'
$plugin_version = $settings['metadata']['plugin_version']

}
