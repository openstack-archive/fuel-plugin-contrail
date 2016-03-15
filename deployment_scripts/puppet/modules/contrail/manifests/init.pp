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
  $node_role        = hiera('role')
  $node_name        = hiera('user_node_name')
  $nodes            = hiera('nodes')

  $public_ssl_hash  = hiera('public_ssl')
  $public_ssl       = $public_ssl_hash['services']

  $neutron_settings = hiera_hash('quantum_settings', {})
  $metadata_secret  = $neutron_settings['metadata']['metadata_proxy_shared_secret']
  $service_token    = $neutron_settings['keystone']['admin_password']
  $nets             = $neutron_settings['predefined_networks']

  $default_ceilometer_hash = { 'enabled' => false }
  $ceilometer_hash         = hiera_hash('ceilometer', $default_ceilometer_hash)

  $keystone    = hiera_hash('keystone', {})
  $admin_token = $keystone['admin_token']

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
  $sriov_hash            = get_sriov_devices()
  $passthrough_whitelist = inline_template(
    '<%= "[" + scope.lookupvar("::contrail::sriov_hash").map{ |dev, _| "{\"devname\":\"#{dev}\", \"physical_network\":\"#{sriov_physnet}\"}" }.join(", ") + "]" %>')

  # Custom mount point for contrail-db
  $cassandra_path = '/var/lib/contrail_db'

  # Control of automatic services startup
  $service_ensure = hiera('upgrade') ? {
    true    => 'stopped',
    default => 'running',
    }

  # Network configuration
  prepare_network_config($network_scheme)
  $interface         = get_network_role_property('neutron/mesh', 'interface')
  $gateway           = $network_scheme['endpoints'][$interface]['gateway']
  $address           = get_network_role_property('neutron/mesh', 'ipaddr')
  $cidr              = get_network_role_property('neutron/mesh', 'cidr')
  $netmask           = get_network_role_property('neutron/mesh', 'netmask')
  $netmask_short     = netmask_to_cidr($netmask)
  $phys_dev          = get_private_ifname($interface)
  $phys_dev_pci      = get_dev_pci_addr($phys_dev)
  $vrouter_core_mask = pick($settings['vrouter_core_mask'], '0x3')

  # DPDK settings
  $global_dpdk_enabled  = $settings['contrail_global_dpdk']
  $compute_dpdk_enabled = $global_dpdk_enabled and 'dpdk' in hiera_array('roles')

  # Package override
  $install_contrail_nova    = pick($settings['install_contrail_nova'], false)
  $install_contrail_qemu_lv = pick($settings['install_contrail_qemu_lv'], false )
  
  if $install_contrail_qemu_lv {
    $libvirt_name = 'libvirt-bin'
  } else {
    $libvirt_name = 'libvird'
  }

  # vCenter settings
  $use_vcenter                                = hiera('use_vcenter', false)
  $vcenter_hash                               = hiera_hash('vcenter_hash', {})
  $contrail_vcenter_datacenter                = $settings['contrail_vcenter_datacenter']
  $contrail_vcenter_dvswitch                  = $settings['contrail_vcenter_dvswitch']
  $contrail_vcenter_dvportgroup               = $settings['contrail_vcenter_dvportgroup']
  $contrail_vcenter_dvportgroup_numberofports = $settings['contrail_vcenter_dvportgroup_numberofports']
  $contrail_vcenter_esxi_for_fabric           = $settings['contrail_vcenter_esxi_for_fabric']

  $mos_mgmt_vip   = $network_metadata['vips']['management']['ipaddr']
  $mos_public_vip = $network_metadata['vips']['public']['ipaddr']

  $contrail_private_vip = $network_metadata['vips']['contrail_priv']['ipaddr']
  $contrail_mgmt_vip    = $contrail_private_vip

  # Settings for RabbitMQ on contrail controllers
  $rabbit             = hiera('rabbit')
  $rabbit_password    = $rabbit['password']
  $rabbit_hosts_ports = hiera('amqp_hosts')

  # RabbitMQ nodes Mgmt IP list
  $rabbit_nodes_hash  = get_nodes_hash_by_roles(hiera('network_metadata'), ['primary-controller', 'controller'])
  $rabbit_ips         = values(get_node_to_ipaddr_map_by_network_role($rabbit_nodes_hash, 'mgmt/messaging'))

  # Contrail DB nodes Private IP list
  $primary_contrail_db_nodes_hash = get_nodes_hash_by_roles(hiera('network_metadata'), ['primary-contrail-db'])
  $primary_contrail_db_ip         = values(get_node_to_ipaddr_map_by_network_role($primary_contrail_db_nodes_hash, 'neutron/mesh'))

  $contrail_db_nodes_hash         = get_nodes_hash_by_roles(hiera('network_metadata'), ['primary-contrail-db', 'contrail-db'])
  $contrail_db_ips                = values(get_node_to_ipaddr_map_by_network_role($contrail_db_nodes_hash, 'neutron/mesh'))

  # Contrail Control nodes Private IP list
  $contrail_control_nodes_hash    = get_nodes_hash_by_roles(hiera('network_metadata'), ['primary-contrail-control', 'contrail-control'])
  $contrail_control_ips           = values(get_node_to_ipaddr_map_by_network_role($contrail_control_nodes_hash, 'neutron/mesh'))

  # Contrail Config nodes Private IP list
  $contrail_config_nodes_hash     = get_nodes_hash_by_roles(hiera('network_metadata'), ['primary-contrail-config', 'contrail-config'])
  $contrail_config_ips            = values(get_node_to_ipaddr_map_by_network_role($contrail_config_nodes_hash, 'neutron/mesh'))
}
