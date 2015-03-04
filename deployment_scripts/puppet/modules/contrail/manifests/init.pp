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
$node_name = hiera('user_node_name')
$nodes= hiera('nodes')

# Network configuration
prepare_network_config($network_scheme)
$ifname = get_private_ifname()
$range_first = $settings['contrail_private_start']
$range_last = $settings['contrail_private_end']
$cidr = $settings['contrail_private_cidr'] # "cidr" is actually a network address with subnet, i.e. 192.168.150.0/24
$netmask=cidr_to_netmask($cidr) # returns i.e. "255.255.255.0"
$netmask_short=netmask_to_cidr($netmask) # returns i.e. "/24"
$address=get_ip_from_range($range_first,$range_last,$netmask_short,$uid,"first")

# Public address
$neutron_settings=hiera('quantum_settings')
$public_cidr=$neutron_settings['predefined_networks']['net04_ext']['L3']['subnet']
$public_first=get_first_ip($public_cidr)
$public_last=get_last_ip($public_cidr)
$public_tmp=split($public_cidr,"/")
$public_prefix=$public_tmp[1] # netmask prefix here
$public_addr=get_ip_from_range($public_first,$public_last,$public_prefix,$uid,'last')

$public_if=$settings['contrail_public_if']

$contrail_node_basename='contrail'
$deployment_node="${contrail_node_basename}-1"

$contrail_node_num = inline_template("<%- 
rv=0
@nodes.each do |node|
if node['user_node_name'] =~ /^#{@contrail_node_basename}-.*/
rv+=1
end
end
-%>
<%= rv %>")
}
