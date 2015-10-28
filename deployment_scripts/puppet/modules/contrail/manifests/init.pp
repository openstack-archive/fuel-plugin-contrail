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
$settings = hiera('contrail', {})

# TODO
#$plugin_version = $settings['metadata']['plugin_version']
$plugin_version = '3.0'
$distribution=$settings['contrail_distribution']

$network_scheme = hiera_hash('network_scheme', {})
$network_metadata = hiera_hash('network_metadata', {})
$uid = hiera('uid')
$master_ip = hiera('master_ip')
$node_role = hiera('role')
$node_name = hiera('user_node_name')
$nodes= hiera('nodes')

$neutron_settings=hiera_hash('quantum_settings', {})
$metadata_secret=$neutron_settings['metadata']['metadata_proxy_shared_secret']
$service_token = $neutron_settings['keystone']['admin_password']
$nets = $neutron_settings['predefined_networks']

$keystone=hiera_hash('keystone', {})
$admin_token = $keystone['admin_token']

$admin_settings = hiera_hash('access', {})
$admin_username = $admin_settings['user']
$admin_password = $admin_settings['password']
$admin_tenant = $admin_settings['tenant']

$mos_mgmt_vip=hiera('management_vip')

# Contrail settings
$asnum = $settings['contrail_asnum']
$external = $settings['contrail_external']
$route_target = $settings['contrail_route_target']

# Network configuration
prepare_network_config($network_scheme)
$ifname = get_private_ifname()
$private_if=get_network_role_property('neutron/mesh', 'interface')
$address=get_network_role_property('neutron/mesh', 'ipaddr')
$cidr=get_network_role_property('neutron/mesh', 'cidr')
$netmask=get_network_role_property('neutron/mesh', 'netmask')
$netmask_short=netmask_to_cidr($netmask)

$mgmt_if=get_network_role_property('management', 'interface')
$mgmt_cidr=get_network_role_property('management', 'cidr')
$mgmt_netmask=get_network_role_property('management', 'netmask')
$mgmt_netmask_short=netmask_to_cidr($mgmt_netmask)

$contrail_mgmt_vip=get_last_ip(hiera('management_network_range'))
$contrail_private_vip=get_last_ip(hiera('private_network_range'))

$contrail_node_basename='contrail'
$deployment_node="${contrail_node_basename}-1"

$contrail_node_num = inline_template("<%-
rv=0
  @nodes.each do |node|
    if (node['user_node_name'] =~ /^#{@contrail_node_basename}-.*/ and node['role'] == 'base-os')
    rv+=1
  end
end
-%>
<%= rv %>")

# Settings for RabbitMQ on contrail controllers
$rabbit=hiera('rabbit')
$rabbit_password=$rabbit['password']
$rabbit_hosts_ports = hiera('amqp_hosts')

# Base-os nodes Private IP list
$baseos_nodes_hash = get_nodes_hash_by_roles($network_metadata, ['base-os'])
$baseos_ips_hash = get_node_to_ipaddr_map_by_network_role($baseos_nodes_hash, 'neutron/mesh')
$baseos_ips = values($baseos_ips_hash)

}
