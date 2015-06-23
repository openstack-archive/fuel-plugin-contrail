#    Copyright 2015 Mirantis, Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

class contrail {

# General configuration
$settings = hiera('contrail')

# TODO
#$plugin_version = $settings['metadata']['plugin_version']
$plugin_version = '1.0'

$network_scheme = hiera('network_scheme')
$uid = hiera('uid')
$master_ip = hiera('master_ip')
$node_role = hiera('role')
$node_name = hiera('user_node_name')
$nodes= hiera('nodes')

$neutron_settings=hiera('quantum_settings')
$metadata_secret=$neutron_settings['metadata']['metadata_proxy_shared_secret']
$neutron_floating=$neutron_settings['predefined_networks']['net04_ext']['L3']['floating']
$service_token = $neutron_settings['keystone']['admin_password']
$keystone=hiera('keystone')
$admin_token = $keystone['admin_token']

$admin_settings = hiera('access')
$admin_username = $admin_settings['user']
$admin_password = $admin_settings['password']

$mos_mgmt_vip=hiera('management_vip')

# Contrail settings
$asnum = $settings['contrail_asnum']
$admin_tenant_private_cidr = $settings['admin_tenant_private_cidr']
$admin_tenant_public_cidr = $settings['admin_tenant_public_cidr']

# Network configuration
prepare_network_config($network_scheme)
$ifname = get_private_ifname()
$private_first = $settings['contrail_private_start']
$private_last = $settings['contrail_private_end']
# "cidr" is actually a network address with subnet, i.e. 192.168.150.0/24
$cidr = $settings['contrail_private_cidr']
$netmask=cidr_to_netmask($cidr) # returns i.e. "255.255.255.0"
$netmask_short=netmask_to_cidr($netmask) # returns i.e. "/24"
$address=get_ip_from_range($private_first,$private_last,$netmask_short,$uid,'first')

$public_network_assignment=hiera('public_network_assignment')
$public_allnodes=$public_network_assignment['assign_to_all_nodes']

if $public_allnodes == true {
  $public_address=get_network_role_property('ex', 'ipaddr')
  $public_netmask=netmask_to_cidr(get_network_role_property('ex', 'netmask'))
}

$default_gw = hiera('management_vrouter_vip')
$private_gw = $settings['contrail_private_gw']
$contrail_mgmt_vip=get_last_ip(get_network_role_property('management', 'cidr'))

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

# Settings for RabbitMQ on contrail controllers
$rabbit=hiera('rabbit')
$rabbit_password=$rabbit['password']

# Returns array of ip addresses
$rabbit_hosts =
split(
  inline_template("<%-
    rv=Array.new
    @nodes.each do |node|
      if node['role'] =~ /^(primary-)?controller$/
        rv << node['internal_address']
      end
    end
  -%>
  <%= rv.join(',') %>")
, ',')
$tmp_rabbit = join($rabbit_hosts,':5673,')
$rabbit_hosts_ports = "${tmp_rabbit}:5673"

}
