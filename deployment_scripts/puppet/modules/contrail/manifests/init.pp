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
  $settings = hiera_hash('contrail', {})

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
  $interface         = get_network_role_property('neutron/mesh', 'interface')
  $routes            = pick($network_scheme['endpoints'][$interface]['routes'], false)

  if  $routes {
    $gateway = $routes[0]['via']
  } else {
    $gateway = false
  }

  $address           = get_network_role_property('neutron/mesh', 'ipaddr')
  $cidr              = get_network_role_property('neutron/mesh', 'cidr')
  $netmask           = get_network_role_property('neutron/mesh', 'netmask')
  $netmask_short     = netmask_to_cidr($netmask)
  $phys_dev          = get_private_ifname($interface, $network_scheme)
  $phys_dev_pci      = get_dev_pci_addr($phys_dev, $network_scheme)
  $phys_dev_mtu      = get_physdev_mtu(regsubst($phys_dev, '\..*' , ''))
  $vrouter_core_mask = pick($settings['vrouter_core_mask'], '0x3')
  $headless_mode     = pick($settings['headless_mode'], true)
  $multi_tenancy     = pick($settings['multi_tenancy'], true)

  # Contrail-API port
  $api_server_port   = pick($settings['api_server_port'], '8082')

  # VIPs
  $mos_mgmt_vip   = $network_metadata['vips']['management']['ipaddr']
  $mos_public_vip = $network_metadata['vips']['public']['ipaddr']

  $contrail_private_vip = $network_metadata['vips']['contrail_priv']['ipaddr']
  $contrail_mgmt_vip    = $contrail_private_vip

  # Public SSL for Contrail WebUI
  $public_ssl_hash    = hiera_hash('public_ssl', {})
  $ssl_hash           = hiera_hash('use_ssl', {})
  $public_ssl         = get_ssl_property($ssl_hash, $public_ssl_hash, 'horizon', 'public', 'usage', false)
  $public_ssl_path    = get_ssl_property($ssl_hash, $public_ssl_hash, 'horizon', 'public', 'path', [''])

  #NOTE(AKirilochkin): Modern way to get the ssl values with understandable variables names
  $public_horizon_endpoint = get_ssl_property($ssl_hash, {}, 'horizon', 'public', 'hostname', [$mos_public_vip])
  $public_horizon_protocol = get_ssl_property($ssl_hash, {}, 'horizon', 'public', 'protocol', 'http')

  $internal_neutron_endpoint = get_ssl_property($ssl_hash, {}, 'neutron', 'internal', 'hostname', [$mos_mgmt_vip])
  $internal_neutron_protocol = get_ssl_property($ssl_hash, {}, 'neutron', 'internal', 'protocol', 'http')

  $internal_glance_endpoint  = get_ssl_property($ssl_hash, {}, 'glance', 'internal', 'hostname', [$mos_mgmt_vip])
  $internal_glance_protocol  = get_ssl_property($ssl_hash, {}, 'glance', 'internal', 'protocol', 'http')

  $internal_cinder_endpoint  = get_ssl_property($ssl_hash, {}, 'cinder', 'internal', 'hostname', [$mos_mgmt_vip])
  $internal_cinder_protocol  = get_ssl_property($ssl_hash, {}, 'cinder', 'internal', 'protocol', 'http')

  $internal_nova_endpoint    = get_ssl_property($ssl_hash, {}, 'nova', 'internal', 'hostname', [$mos_mgmt_vip])
  $internal_nova_protocol    = get_ssl_property($ssl_hash, {}, 'nova', 'internal', 'protocol', 'http')

  $internal_auth_address     = get_ssl_property($ssl_hash, {}, 'keystone', 'internal', 'hostname', [hiera('service_endpoint', ''), $mos_mgmt_vip])
  $internal_auth_protocol    = get_ssl_property($ssl_hash, {}, 'keystone', 'internal', 'protocol', 'http')

  #NOTE(AKirilochkin): There are duplicate variables with the different names, we have
  # to switch to one format

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

  # Custom mount point for contrail-db
  $cassandra_path = '/var/lib/contrail_db'

  # Control of automatic services startup
  $service_ensure = hiera('upgrade',false) ? {
    true    => 'stopped',
    default => 'running',
  }

  # DPDK settings
  $global_dpdk_enabled  = $settings['contrail_global_dpdk']
  $compute_dpdk_enabled = $global_dpdk_enabled and 'dpdk' in hiera_array('roles')

  # Package override
  $patch_nova               = pick($settings['patch_nova'], false)
  $patch_nova_vmware        = pick($settings['patch_nova_vmware'], false)
  $install_contrail_qemu_lv = pick($settings['install_contrail_qemu_lv'], false )

  if $install_contrail_qemu_lv and $compute_dpdk_enabled {
    $libvirt_name = 'libvirt-bin'
  } else {
    $libvirt_name = 'libvirtd'
  }

  # vCenter settings
  $use_vcenter  = hiera('use_vcenter', false)
  $vcenter_hash = hiera_hash('vcenter', {})

  if $use_vcenter {
    $mode                                       = 'vcenter'
    $orchestrator                               = 'openstack'
    $hypervisor                                 = 'libvirt'
    $vmdk_vm_image                              = pick($settings['vmdk_vm_image'], "http://${::contrail::master_ip}:8080/plugins/contrail-3.0/ContrailVM-disk1.vmdk")
    $vcenter_server_ip                          = $vcenter_hash['computes'][0]['vc_host']
    $vcenter_server_user                        = $vcenter_hash['computes'][0]['vc_user']
    $vcenter_server_pass                        = $vcenter_hash['computes'][0]['vc_password']
    $vcenter_server_name                        = $vcenter_hash['computes'][0]['availability_zone_name']
    $contrail_vcenter_datacenter                = $settings['contrail_vcenter_datacenter']
    $contrail_vcenter_dvswitch                  = $settings['contrail_vcenter_dvswitch']
    $contrail_vcenter_dvportgroup               = $settings['contrail_vcenter_dvportgroup']
    $contrail_vcenter_dvportgroup_numberofports = $settings['contrail_vcenter_dvportgroup_numberofports']
    $contrail_vcenter_esxi_for_fabric           = $settings['contrail_vcenter_esxi_for_fabric']
    $provision_vmware                           = $settings['provision_vmware']
    $contrailvm_ntp                             = $settings['contrailvm_ntp']
    $provision_vmware_type                      = $settings['provision_vmware_type']
    $contrail_vcenter_vm_ips                    = get_contrailvm_ips()
    $contrail_compute_vmware_nodes_hash         = get_nodes_hash_by_roles($network_metadata, ['compute-vmware'])
    $contrail_compute_vmware_ips                = values(get_node_to_ipaddr_map_by_network_role($contrail_compute_vmware_nodes_hash, 'neutron/mesh'))
    $primary_controller_role                    = hiera('primary_controller_role', ['primary-controller'])
    $contrail_fab_build_node_hash               = get_nodes_hash_by_roles($network_metadata, $primary_controller_role)
    $contrail_fab_build_ip                      = values(get_node_to_ipaddr_map_by_network_role($contrail_fab_build_node_hash, 'neutron/mesh'))
    $contrail_fab_default                       = {'vmdk' => '/opt/contrail/ContrailVM-disk1.vmdk', 'vcenter_server' => 'vcenter1', 'mode' => $mode }
  }

  # Settings for RabbitMQ on contrail controllers
  $rabbit             = hiera_hash('rabbit')
  $rabbit_password    = $rabbit['password']
  $rabbit_hosts_ports = hiera('amqp_hosts')

  # RabbitMQ nodes Mgmt IP list
  $rabbit_ips            = split(inline_template("<%= @rabbit_hosts_ports.split(',').map {|c| c.strip.gsub(/:[0-9]*$/,'')}.join(',') %>"),',')

  # Contrail DB nodes Private IP list
  $primary_contrail_db_nodes_hash = get_nodes_hash_by_roles($network_metadata, ['primary-contrail-db'])
  $primary_contrail_db_ip         = sort(values(get_node_to_ipaddr_map_by_network_role($primary_contrail_db_nodes_hash, 'neutron/mesh')))

  $contrail_db_nodes_hash         = get_nodes_hash_by_roles($network_metadata, ['primary-contrail-db', 'contrail-db'])
  $contrail_db_ips                = sort(values(get_node_to_ipaddr_map_by_network_role($contrail_db_nodes_hash, 'neutron/mesh')))

  # Contrail Control nodes Private IP list
  $contrail_control_nodes_hash    = get_nodes_hash_by_roles($network_metadata, ['primary-contrail-control', 'contrail-control'])
  $contrail_control_ips           = sort(values(get_node_to_ipaddr_map_by_network_role($contrail_control_nodes_hash, 'neutron/mesh')))

  # Contrail Config nodes Private IP list
  $contrail_config_nodes_hash     = get_nodes_hash_by_roles($network_metadata, ['primary-contrail-config', 'contrail-config'])
  $contrail_config_ips            = sort(values(get_node_to_ipaddr_map_by_network_role($contrail_config_nodes_hash, 'neutron/mesh')))
  $contrail_config_ips_adm        = sort(values(get_node_to_ipaddr_map_by_network_role($contrail_config_nodes_hash, 'fw-admin')))

  # Cassandra, Kafka & Zookeeper servers list
  $cassandra_server_list      = inline_template("<%= scope.lookupvar('contrail::contrail_db_ips').map{ |ip| \"#{ip}:9042\" }.join(' ') %>")
  $cassandra_server_list_9160 = inline_template("<%= scope.lookupvar('contrail::contrail_db_ips').map{ |ip| \"#{ip}:9160\" }.join(' ') %>")
  $kafka_broker_list          = inline_template("<%= scope.lookupvar('contrail::contrail_db_ips').map{ |ip| \"#{ip}:9092\" }.join(' ') %>")
  $zk_server_ip               = inline_template("<%= scope.lookupvar('contrail::contrail_db_ips').map{ |ip| \"#{ip}:2181\" }.join(',') %>")
}
