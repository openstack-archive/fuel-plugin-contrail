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
  $interface         = pick(get_network_role_property('neutron/mesh', 'interface'), 'br-mesh')

  #fallback to vhost0 for day2 scenario
  $iface = pick($network_scheme['endpoints'][$interface], $network_scheme['endpoints']['vhost0'], {})
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
  $raw_phys_dev      = regsubst($phys_dev, '\..*' , '')
  $dev_mac           = getvar("::macaddress_${raw_phys_dev}")
  $vrouter_core_mask = pick($settings['vrouter_core_mask'], '0x3')
  #if user specify particular cpu's for vrouter - taskset command should differ
  if $vrouter_core_mask =~ /^0x[0-9a-zA-Z]/ {
    $taskset_command  = "taskset ${vrouter_core_mask}"
  } else {
    $taskset_command  = "taskset -c ${vrouter_core_mask}"
  }

  $headless_mode     = pick($settings['headless_mode'], true)
  $vr_flow_entries   = pick($settings['vr_flow_entries'], '524288')
  $vr_mpls_labels    = pick($settings['vr_mpls_labels'], '5120')
  $log_flow          = pick($settings['log_flow'], '0')

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

  if $ssl_hash['contrail'] {
    $service_name = 'contrail'
    } else {
    $service_name = 'horizon'
  }

  $public_ssl         = get_ssl_property($ssl_hash, $public_ssl_hash, $service_name, 'public', 'usage', false)
  $public_ssl_path    = get_ssl_property($ssl_hash, $public_ssl_hash, $service_name, 'public', 'path', [''])

  #NOTE(AKirilochkin): Modern way to get the ssl values with understandable variables names
  $public_horizon_endpoint   = get_ssl_property($ssl_hash, {}, 'horizon', 'public', 'hostname', [$mos_public_vip])
  $public_horizon_protocol   = get_ssl_property($ssl_hash, {}, 'horizon', 'public', 'protocol', 'http')

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
  $keystone_insecure  = pick($settings['keystone_insecure'], true)

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
  $asnum                     = $settings['contrail_asnum']
  $external                  = $settings['contrail_external']
  $route_target              = $settings['contrail_route_target']
  $gateways                  = split($settings['contrail_gateways'], ',')
  $gr_enable                 = pick($settings['graceful_restart_enable'], false)
  $gr_timer                  = pick($settings['graceful_restart_time'], 300)
  $llgr_timer                = pick($settings['long_lived_graceful_restart_time'], 300)
  $eor_timeout               = pick($settings['end_of_rib_timeout'], 300)
  $gr_bgp_helper_enable      = pick($settings['graceful_restart_bgp_helper_enable'], false)

  # BGP settings
  $bgpaas_port_start = pick($settings['bgpaas_port_start'], '50000')
  $bgpaas_port_end   = pick($settings['bgpaas_port_end'], '50512')

  # Kafka settings
  $kafka_log_retention_bytes        = pick($settings['kafka_log_retention_bytes'], '1073741824')
  $kafka_log_segment_bytes          = pick($settings['kafka_log_segment_bytes'], '1073741824')
  $kafka_log_cleanup_policy         = pick($settings['kafka_log_cleanup_policy'], 'compact')
  $kafka_log_cleaner_threads        = pick($settings['kafka_log_cleaner_threads'], '2')
  $kafka_cleaner_dedupe_buffer_size = pick($settings['kafka_cleaner_dedupe_buffer_size'], '250000000')
  $kafka_partitions                 = pick($settings['kafka_partitions'], '30')
  $kafka_retention_hours            = pick($settings['kafka_retention_hours'], '24')

  # Lbaas version
  $lbaas_plugin_version = pick($settings['lbaas_plugin_version'], 'neutron_plugin_contrail.plugins.opencontrail.loadbalancer.v2.plugin.LoadBalancerPluginV2')

  # Memcached settings
  $memcached_enabled = pick($settings['memcached_enabled'], true)


  $discovery_hc_max_miss       = pick($settings['discovery_hc_max_miss'], '3')

  $tls_xmpp_enable           = pick($settings['tls_xmpp_enable'], false)
  if $tls_xmpp_enable {
    $tls_xmpp_wildcard_crt = pick($settings['tls_xmpp_wildcard_crt'], 'No cert provided!')
    $tls_xmpp_wildcard_key = pick($settings['tls_xmpp_wildcard_key'], 'No key provided!')
    $tls_xmpp_ca_crt       = pick($settings['tls_xmpp_ca_crt'], 'No CA provided!')
  }

  # Custom mount point for contrail-db
  $cassandra_path = '/var/lib/contrail_db'
  $cassandra_compaction_throughput = pick($settings['cassandra_compaction_throughput'], '16')

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

  if $install_contrail_qemu_lv {
    $libvirt_name = 'libvirt-bin'
  } else {
    $libvirt_name = 'libvirtd'
  }

  # vCenter settings
  $use_vcenter  = hiera('use_vcenter', false)
  $vcenter_hash = hiera_hash('vcenter', {})

  if $use_vcenter {
    $mode                               = 'vcenter'
    $orchestrator                       = 'openstack'
    $hypervisor                         = 'libvirt'
    $vcenter_server_ip                  = pick($vcenter_hash['computes'][0]['vc_host'], '192.168.0.1')
    $vcenter_server_user                = pick($vcenter_hash['computes'][0]['vc_user'], 'admin')
    $vcenter_server_pass                = pick($vcenter_hash['computes'][0]['vc_password'], 'admin')
    $vcenter_server_name                = pick($vcenter_hash['computes'][0]['availability_zone_name'], 'vcenter')
    $contrail_vcenter_datacenter        = pick($settings['contrail_vcenter_datacenter'], 'datacenter')
    $dvs_internal                       = pick($settings['dvs_internal'], 'Contrail-DVS-Int')
    $dvs_internal_pg                    = "${dvs_internal}-PG"
    $dvs_private                        = pick($settings['dvs_private'], 'Contrail-DVS-Priv')
    $dvs_private_pg                     = "${dvs_private}-PG"
    $contrail_compute_vmware_nodes_hash = get_nodes_hash_by_roles($network_metadata, ['compute-vmware'])
    $contrail_compute_vmware_ips        = values(get_node_to_ipaddr_map_by_network_role($contrail_compute_vmware_nodes_hash, 'neutron/mesh'))
    $contrail_vmware_nodes_hash         = get_nodes_hash_by_roles($contrail::network_metadata, ['contrail-vmware'])
    $contrail_vcenter_vm_ips            = sort(values(get_node_to_ipaddr_map_by_network_role($contrail_vmware_nodes_hash, 'neutron/mesh')))
  }

  # Settings for RabbitMQ on contrail controllers
  $rabbit             = hiera_hash('rabbit')
  $rabbit_password    = $rabbit['password']
  $rabbit_hosts_ports = hiera('amqp_hosts')

  # RabbitMQ nodes Mgmt IP list
  $rabbit_ips = split(inline_template("<%= @rabbit_hosts_ports.split(',').map {|c| c.strip.gsub(/:[0-9]*$/,'')}.join(',') %>"),',')

  # Contrail DB nodes Private IP list
  $primary_contrail_db_nodes_hash = get_nodes_hash_by_roles($network_metadata, ['primary-contrail-db'])
  $primary_contrail_db_ip         = ipsort(values(get_node_to_ipaddr_map_by_network_role($primary_contrail_db_nodes_hash, 'neutron/mesh')))

  $contrail_db_roles              = hiera('contrail_db_roles', ['primary-contrail-db', 'contrail-db'])
  $contrail_db_nodes_hash         = get_nodes_hash_by_roles($network_metadata, $contrail_db_roles)
  $contrail_db_ips                = ipsort(values(get_node_to_ipaddr_map_by_network_role($contrail_db_nodes_hash, 'neutron/mesh')))


  # Dedicated Analytics DB
  $primary_analytics_db_nodes_hash = get_nodes_hash_by_roles($network_metadata, ['primary-contrail-analytics-db'])
  $primary_analytics_db_ip         = ipsort(values(get_node_to_ipaddr_map_by_network_role($primary_analytics_db_nodes_hash, 'neutron/mesh')))

  $analytics_db_roles              = hiera('contrail_analytics_db_roles', ['primary-contrail-analytics-db', 'contrail-analytics-db'])
  $analytics_db_nodes_hash         = get_nodes_hash_by_roles($network_metadata, $analytics_db_roles)
  $analytics_db_ips                = ipsort(values(get_node_to_ipaddr_map_by_network_role($analytics_db_nodes_hash, 'neutron/mesh')))


  # Contrail Control nodes Private IP list
  $contrail_control_nodes_hash = get_nodes_hash_by_roles($network_metadata, ['primary-contrail-control', 'contrail-control'])
  $contrail_control_ips        = ipsort(values(get_node_to_ipaddr_map_by_network_role($contrail_control_nodes_hash, 'neutron/mesh')))

  # Contrail Config nodes Private IP list
  $contrail_config_nodes_hash = get_nodes_hash_by_roles($network_metadata, ['primary-contrail-config', 'contrail-config'])
  $contrail_config_ips        = ipsort(values(get_node_to_ipaddr_map_by_network_role($contrail_config_nodes_hash, 'neutron/mesh')))
  $contrail_config_ips_adm    = ipsort(values(get_node_to_ipaddr_map_by_network_role($contrail_config_nodes_hash, 'fw-admin')))

  # Contrail Analytics nodes Private IP list
  $contrail_analytics_nodes_hash     = get_nodes_hash_by_roles($network_metadata, ['primary-contrail-analytics', 'contrail-analytics'])
  $contrail_analytics_ips            = sort(values(get_node_to_ipaddr_map_by_network_role($contrail_analytics_nodes_hash, 'neutron/mesh')))

  # Cassandra, Kafka & Zookeeper servers list
  $contrail_db_list           = inline_template("<%= scope.lookupvar('contrail::contrail_db_ips').map{ |ip| \"#{ip}:9042\" }.join(' ') %>")
  $contrail_db_list_9160      = inline_template("<%= scope.lookupvar('contrail::contrail_db_ips').map{ |ip| \"#{ip}:9160\" }.join(' ') %>")
  $analytics_db_list          = inline_template("<%= scope.lookupvar('contrail::analytics_db_ips').map{ |ip| \"#{ip}:9042\" }.join(' ') %>")
  $analytics_db_list_9160     = inline_template("<%= scope.lookupvar('contrail::analytics_db_ips').map{ |ip| \"#{ip}:9160\" }.join(' ') %>")
  $kafka_broker_list          = inline_template("<%= scope.lookupvar('contrail::analytics_db_ips').map{ |ip| \"#{ip}:9092\" }.join(' ') %>")
  $zk_server_ip               = inline_template("<%= scope.lookupvar('contrail::contrail_db_ips').map{ |ip| \"#{ip}:2181\" }.join(',') %>")

  $zk_ticktime                = pick($settings['zk_ticktime'], 2000)
  $zk_initlimit               = pick($settings['zk_initlimit'], 10)
  $zk_synclimit               = pick($settings['zk_synclimit'], 5)
  $zk_datadir                 = pick($settings['zk_datadir'], '/var/lib/zookeeper')
  $zk_clientport              = pick($settings['zk_clientport'], 2181)
  $zk_maxsessiontimeout       = pick($settings['zk_maxsessiontimeout'], 120000)
  $zk_autopurge_purgeinterval = pick($settings['zk_autopurge_purgeinterval'], '0')

  # Perfomance tuning
  $cassandra_rpc_max_threads = pick($settings['cassandra_rpc_max_threads'], false)

  #Cassandra limits settings
  $cassandra_memlock_limit = pick($settings['cassandra_memlock_limit'], 'unlimited')
  $cassandra_nofile_limit  = pick($settings['cassandra_nofile_limit'], '100000')
  $cassandra_as_limit      = pick($settings['cassandra_as_limit'], 'unlimited')
  $cassandra_nproc_limit   = pick($settings['cassandra_nproc_limit'], '8096')

  # Vrouter logging settings
  $use_syslog      = pick($settings['use_syslog'], '1')
  $syslog_facility = pick($settings['syslog_facility'], 'LOG_LOCAL0')
  $log_level       = pick($settings['log_level'], 'SYS_INFO')

  #minfds settings
  $supervisor_config_minfds    = pick($settings['supervisor_config_minfds'], '65535')
  $supervisor_control_minfds   = pick($settings['supervisor_control_minfds'], '10240')
  $supervisor_analytics_minfds = pick($settings['supervisor_analytics_minfds'], '65535')

  $aaa_mode = pick($settings['aaa_mode'], 'cloud-admin')

  #Sandesh settings
  $sandesh_send_rate_limit = pick($settings['sandesh_send_rate_limit'], '10')

  $analytics_config_audit_ttl = pick($settings['analytics_config_audit_ttl'], '2160')
  $analytics_statistics_ttl   = pick($settings['analytics_statistics_ttl'], '24')
  $analytics_flow_ttl         = pick($settings['analytics_flow_ttl'], '2')
  $analytics_data_ttl         = pick($settings['analytics_data_ttl'], '48')

  $analytics_keyspace = 'ContrailAnalyticsCql'
  $analytics_tables = [
    'flowrecordtable',
    'flowtablevrouterver2',
    'statstablebydbltagv3',
    'objectvaluetable',
    'messagetablemessagetype',
    'messagetablekeyword',
    'messagetabletimestamp',
    'messagetablecategory',
    'statstablebyu64strtagv3',
    'statstablebyu64tagv3',
    'messagetablesource',
    'statstablebystrstrtagv3',
    'systemobjecttable',
    'flowtableprotdpver2',
    'statstablebystru64tagv3',
    'objecttable',
    'statstablebyu64u64tagv3',
    'flowtabledvndipver2',
    'messagetable',
    'statstablebystrtagv3',
    'flowtableprotspver2',
    'flowtablesvnsipver2',
    'messagetablemoduleid'
  ]
}


