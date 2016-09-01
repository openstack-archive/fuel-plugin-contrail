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
  $distribution   = 'juniper'

  $network_scheme   = hiera_hash('network_scheme', {})
  $network_metadata = hiera_hash('network_metadata', {})
  $uid              = hiera('uid')
  $master_ip        = hiera('master_ip')
  $node_name        = hiera('user_node_name')
  $nodes            = hiera('nodes')
  $region           = hiera('region', 'RegionOne')
  $dpdk_hash        = hiera_hash('dpdk', {})

  # Network configuration
  prepare_network_config($network_scheme)
  $interface         = pick(get_network_role_property('neutron/mesh', 'interface'), 'br-mesh')

  $iface = pick($network_scheme['endpoints'][$interface], {})
  $routes = pick($iface['routes'], false)

  if $routes {
    $gateway = $routes[0]['via']
  } else {
    $gateway = false
  }

  $address           = pick(get_network_role_property('neutron/mesh', 'ipaddr'), get_network_role_property('contrail/vhost0', 'ipaddr'))
  $cidr              = pick(get_network_role_property('neutron/mesh', 'cidr'), get_network_role_property('contrail/vhost0', 'cidr'))
  $netmask           = pick(get_network_role_property('neutron/mesh', 'netmask'), get_network_role_property('contrail/vhost0', 'netmask'))
  $netmask_short     = netmask_to_cidr($netmask)
  $phys_dev          = get_private_ifname($interface, $network_scheme)
  $phys_dev_pci      = get_dev_pci_addr($phys_dev, $network_scheme)
  $phys_dev_mtu      = get_physdev_mtu(regsubst($phys_dev, '\..*' , ''))
  $vrouter_core_mask = pick($settings['vrouter_core_mask'], '0x3')

  # VIPs
  $mos_mgmt_vip   = $network_metadata['vips']['management']['ipaddr']
  $mos_public_vip = $network_metadata['vips']['public']['ipaddr']

  $contrail_private_vip = $network_metadata['vips']['contrail_priv']['ipaddr']
  $contrail_mgmt_vip    = $contrail_private_vip

  $contrail_api_public_port  = $settings['contrail_api_public_port']

  # Public SSL for Contrail WebUI
  $public_ssl_hash    = hiera_hash('public_ssl', {})
  $ssl_hash           = hiera_hash('use_ssl', {})
  $public_ssl         = get_ssl_property($ssl_hash, $public_ssl_hash, 'horizon', 'public', 'usage', false)
  $public_ssl_path    = get_ssl_property($ssl_hash, $public_ssl_hash, 'horizon', 'public', 'path', [''])

  # Internal SSL for keystone connections
  $keystone_ssl       = get_ssl_property($ssl_hash, {}, 'keystone', 'admin', 'usage', false)
  $keystone_protocol  = get_ssl_property($ssl_hash, {}, 'keystone', 'admin', 'protocol', 'http')
  $keystone_address   = get_ssl_property($ssl_hash, {}, 'keystone', 'admin', 'hostname', [$mos_mgmt_vip])
  $auth_url           = "${keystone_protocol}://${keystone_address}:35357/v2.0"

  $neutron_ssl      = get_ssl_property($ssl_hash, {}, 'neutron', 'admin', 'usage', false)
  $neutron_protocol = get_ssl_property($ssl_hash, {}, 'neutron', 'admin', 'protocol', 'http')
  $neutron_config   = hiera_hash('neutron_config', {})
  $floating_net     = try_get_value($neutron_config, 'default_floating_net', 'net04_ext')
  $private_net      = try_get_value($neutron_config, 'default_private_net', 'net04')
  $default_router   = try_get_value($neutron_config, 'default_router', 'router04')
  $nets             = $neutron_config['predefined_networks']
  $neutron_user     = pick($neutron_config['keystone']['admin_user'], 'neutron')
  $service_token    = $neutron_config['keystone']['admin_password']
  $service_tenant   = pick($neutron_config['keystone']['admin_tenant'], 'services')

  $default_ceilometer_hash = { 'enabled' => false }
  $ceilometer_hash         = hiera_hash('ceilometer', $default_ceilometer_hash)
  $ceilometer_ha_mode      = pick($ceilometer_hash['ha_mode'], true)

  $keystone        = hiera_hash('keystone', {})
  $admin_token     = $keystone['admin_token']
  $metadata_secret = $neutron_config['metadata']['metadata_proxy_shared_secret']

  $admin_settings = hiera_hash('access', {})
  $admin_username = $admin_settings['user']
  $admin_password = $admin_settings['password']
  $admin_tenant   = $admin_settings['tenant']

  # Contrail settings
  $asnum            = $settings['contrail_asnum']
  $external         = $settings['contrail_external']
  $route_target     = $settings['contrail_route_target']
  $gateways         = split($settings['contrail_gateways'], ',')
  # Hugepages configuration for DPDK vrouter
  $hugepages_size   = pick($settings['hugepages_size'],2)
  $hugepages_amount = pick($settings['hugepages_amount'],10)
  $hugepages_number = floor($::memorysize_mb * $hugepages_amount / '100' / $hugepages_size)

  # SRIOV settings
  $global_sriov_enabled  = $settings['contrail_global_sriov']
  $compute_sriov_enabled = $global_sriov_enabled and 'sriov' in hiera_array('roles')
  $sriov_physnet         = $settings['sriov_physnet']

  # DPDK settings
  $global_dpdk_enabled  = $settings['contrail_global_dpdk']
  $dpdk_on_vf           = $settings['dpdk_on_vf']
  $compute_dpdk_enabled = $global_dpdk_enabled and 'dpdk' in hiera_array('roles')

  # DPDK on VF settings
  $compute_dpkd_on_vf    = $compute_dpdk_enabled and $compute_sriov_enabled and $settings['dpdk_on_vf']
  $dpdk_vf_number        = 0


  # ToR agent settings
  $enable_tor_agents  = $settings['enable_tor_agents']
  $tor_agents_ssl  = $settings['tor_agents_ssl']
  if $enable_tor_agents == true {
    $tor_agents_configurations = parseyaml($settings['tor_agents_configurations'])
  }


  # Custom mount point for contrail-db
  $cassandra_path = '/var/lib/contrail_db'

  # Control of automatic services startup
  $service_ensure = hiera('upgrade',false) ? {
    true    => 'stopped',
    default => 'running',
  }

  # Package override
  $patch_nova               = pick($settings['patch_nova'], false)
  $install_contrail_qemu_lv = pick($settings['install_contrail_qemu_lv'], false )

  if $install_contrail_qemu_lv and ( $compute_dpdk_enabled or $compute_sriov_enabled ) {
    $libvirt_name = 'libvirt-bin'
  } else {
    $libvirt_name = 'libvirtd'
  }

  # Settings for RabbitMQ on contrail controllers
  $rabbit             = hiera_hash('rabbit')
  $rabbit_password    = $rabbit['password']
  $rabbit_hosts_ports = hiera('amqp_hosts')

  # RabbitMQ nodes Mgmt IP list
  $rabbit_ips            = split(inline_template("<%= @rabbit_hosts_ports.split(',').map {|c| c.strip.gsub(/:[0-9]*$/,'')}.join(',') %>"),',')

  # Contrail DB nodes Private IP list
  $primary_contrail_db_nodes_hash = get_nodes_hash_by_roles($network_metadata, ['primary-contrail-db'])
  $primary_contrail_db_ip         = ipsort(values(get_node_to_ipaddr_map_by_network_role($primary_contrail_db_nodes_hash, 'neutron/mesh')))

  $contrail_db_roles              = hiera('contrail_db_roles', ['primary-contrail-db', 'contrail-db'])
  $contrail_db_nodes_hash         = get_nodes_hash_by_roles($network_metadata, $contrail_db_roles)
  $contrail_db_ips                = ipsort(values(get_node_to_ipaddr_map_by_network_role($contrail_db_nodes_hash, 'neutron/mesh')))

  # Dedicated Analytics DB
  $dedicated_analytics_db = pick($settings['dedicated_analytics_db'], false)

  if $dedicated_analytics_db {
    $primary_analytics_db_nodes_hash = get_nodes_hash_by_roles($network_metadata, ['primary-contrail-analytics-db'])
    $primary_analytics_db_ip         = ipsort(values(get_node_to_ipaddr_map_by_network_role($primary_analytics_db_nodes_hash, 'neutron/mesh')))

    $analytics_db_roles              = hiera('contrail_analytics_db_roles', ['primary-contrail-analytics-db', 'contrail-analytics-db'])
    $analytics_db_nodes_hash         = get_nodes_hash_by_roles($network_metadata, $analytics_db_roles)
    $analytics_db_ips                = ipsort(values(get_node_to_ipaddr_map_by_network_role($analytics_db_nodes_hash, 'neutron/mesh')))
  } else {
    $analytics_db_ips                = $contrail_db_ips
  }

  # Contrail Control nodes Private IP list
  $contrail_control_roles         = hiera('contrail_control_roles', ['primary-contrail-control', 'contrail-control'])
  $contrail_control_nodes_hash    = get_nodes_hash_by_roles($network_metadata, $contrail_control_roles)
  $contrail_control_ips           = ipsort(values(get_node_to_ipaddr_map_by_network_role($contrail_control_nodes_hash, 'neutron/mesh')))

  # Contrail Config nodes Private IP list
  $contrail_config_roles          = hiera('contrail_config_roles', ['primary-contrail-config', 'contrail-config'])
  $contrail_config_nodes_hash     = get_nodes_hash_by_roles($network_metadata, $contrail_config_roles)
  $contrail_config_ips            = ipsort(values(get_node_to_ipaddr_map_by_network_role($contrail_config_nodes_hash, 'neutron/mesh')))

  # Contrail Analytics nodes Private IP list
  $contrail_analytics_roles       = hiera('contrail_analytics_roles', ['primary-contrail-analytics', 'contrail-analytics'])
  $contrail_analytics_nodes_hash  = get_nodes_hash_by_roles($network_metadata, $contrail_analytics_roles)
  $contrail_analytics_ips         = ipsort(values(get_node_to_ipaddr_map_by_network_role($contrail_analytics_nodes_hash, 'neutron/mesh')))

  # Cassandra, Kafka & Zookeeper servers list
  $contrail_db_list           = inline_template("<%= scope.lookupvar('contrail::contrail_db_ips').map{ |ip| \"#{ip}:9042\" }.join(' ') %>")
  $contrail_db_list_9160      = inline_template("<%= scope.lookupvar('contrail::contrail_db_ips').map{ |ip| \"#{ip}:9160\" }.join(' ') %>")
  $analytics_db_list          = inline_template("<%= scope.lookupvar('contrail::analytics_db_ips').map{ |ip| \"#{ip}:9042\" }.join(' ') %>")
  $analytics_db_list_9160     = inline_template("<%= scope.lookupvar('contrail::analytics_db_ips').map{ |ip| \"#{ip}:9160\" }.join(' ') %>")
  $kafka_broker_list          = inline_template("<%= scope.lookupvar('contrail::analytics_db_ips').map{ |ip| \"#{ip}:9092\" }.join(' ') %>")
  $zk_server_ip               = inline_template("<%= scope.lookupvar('contrail::contrail_db_ips').map{ |ip| \"#{ip}:2181\" }.join(',') %>")

  # vCenter settings
  $vcenter_hash                               = hiera_hash('vcenter', false)
  if $vcenter_hash {
    $vcenter_server_ip                          = $vcenter_hash['computes'][0]['vc_host']
    $vcenter_server_user                        = $vcenter_hash['computes'][0]['vc_user']
    $vcenter_server_pass                        = $vcenter_hash['computes'][0]['vc_password']
    $vcenter_server_cluster                     = $vcenter_hash['computes'][0]['vc_cluster']
    $vcenter_server_name                        = $vcenter_hash['computes'][0]['availability_zone_name']
    $contrail_vcenter_datacenter                = pick($settings['contrail_vcenter_datacenter'], 'Datacenter')
    $dvs_external                               = 'Contrail-DVS-Ext'
    $dvs_internal                               = 'Contrail-DVS-Int'
  }

}
