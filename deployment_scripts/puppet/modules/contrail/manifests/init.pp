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
$nets = $neutron_settings['ostf_nets']

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
$gateways = split($settings['contrail_gateways'], ',')

# Network configuration
prepare_network_config($network_scheme)
$phys_dev=get_network_role_property('neutron/mesh', 'phys_dev')
$interface=get_network_role_property('neutron/mesh', 'interface')
$gateway=$network_scheme['endpoints'][$interface]['gateway']
$address=get_network_role_property('neutron/mesh', 'ipaddr')
$cidr=get_network_role_property('neutron/mesh', 'cidr')
$netmask=get_network_role_property('neutron/mesh', 'netmask')
$netmask_short=netmask_to_cidr($netmask)

$mgmt_if=get_network_role_property('management', 'interface')
$mgmt_cidr=get_network_role_property('management', 'cidr')
$mgmt_netmask=get_network_role_property('management', 'netmask')
$mgmt_netmask_short=netmask_to_cidr($mgmt_netmask)

$contrail_private_vip=$network_metadata['vips']['contrail_priv']['ipaddr']
$contrail_mgmt_vip=$contrail_private_vip

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

# Contrail DB nodes Private IP list
$primary_contrail_db_nodes_hash = get_nodes_hash_by_roles(hiera('network_metadata'), ['primary-contrail-db'])
$primary_contrail_db_ip         = pick(values(get_node_to_ipaddr_map_by_network_role($primary_contrail_db_nodes_hash, 'neutron/mesh')))

$contrail_db_nodes_hash         = get_nodes_hash_by_roles(hiera('network_metadata'), ['primary-contrail-db', 'contrail-db'])
$contrail_db_ips                = values(get_node_to_ipaddr_map_by_network_role($contrail_db_nodes_hash, 'neutron/mesh'))

# Contrail Control nodes Private IP list
$contrail_control_nodes_hash    = get_nodes_hash_by_roles(hiera('network_metadata'), ['primary-contrail-control', 'contrail-control'])
$contrail_control_ips           = values(get_node_to_ipaddr_map_by_network_role($contrail_control_nodes_hash, 'neutron/mesh'))

# Contrail Config nodes Private IP list
$contrail_config_nodes_hash     = get_nodes_hash_by_roles(hiera('network_metadata'), ['primary-contrail-config', 'contrail-config'])
$contrail_config_ips            = values(get_node_to_ipaddr_map_by_network_role($contrail_config_nodes_hash, 'neutron/mesh'))
}
