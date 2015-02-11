class contrail {

# General configuration
$settings = hiera('contrail')

# TODO
#$plugin_version = $settings['metadata']['plugin_version']
$plugin_version = '1.0.0'

$network_scheme = hiera('network_scheme')
$uid = hiera('uid')
$master_ip = hiera('master_ip')
$node_role = hiera('role')

# Network configuration
prepare_network_config($network_scheme)
$ifname = get_private_ifname()
$range_first = $settings['contrail_private_start']
$range_last = $settings['contrail_private_end']
$cidr = $settings['contrail_private_cidr'] # "cidr" is actually a network address with subnet, i.e. 192.168.150.0/24
$netmask=cidr_to_netmask($cidr) # returns i.e. "255.255.255.0"
$netmask_short=netmask_to_cidr($netmask) # returns i.e. "/24"
$address=get_ip_from_range($range_first,$range_last,$netmask,$uid)

}
