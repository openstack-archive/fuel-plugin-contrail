class contrail::endpoints {

  notice('MODULAR: contrail/endpoints.pp')

  $contrail = hiera_hash('contrail', {})
  $neutron_hash  = hiera_hash('neutron', {})
  $use_contrail = $contrail['metadata']['enabled']

  if $use_contrail {

    $public_vip        = $contrail::mos_public_vip
    $management_vip    = $contrail::contrail_mgmt_vip
    $internal_vip      = $contrail::contrail_private_vip

    $public_ssl_hash   = hiera_hash('public_ssl')
    $ssl_hash          = hiera_hash('use_ssl', {})

    $public_protocol   = get_ssl_property($ssl_hash, $public_ssl_hash, 'contrail', 'public', 'protocol', 'http')
    $internal_protocol = get_ssl_property($ssl_hash, {}, 'contrail', 'internal', 'protocol', 'http')
    $admin_protocol    = get_ssl_property($ssl_hash, {}, 'contrail', 'admin', 'protocol', 'http')

    $public_address    = get_ssl_property($ssl_hash, $public_ssl_hash, 'contrail', 'public', 'hostname', [$public_vip])
    $internal_address  = get_ssl_property($ssl_hash, {}, 'contrail', 'internal', 'hostname', [$management_vip])
    $admin_address     = get_ssl_property($ssl_hash, {}, 'contrail', 'admin', 'hostname', [$internal_vip])

    $region = hiera('region', 'RegionOne')
    $tenant = "services"

    # Config service
    $config_port = $contrail::api_server_port
    keystone::resource::service_identity { 'contrail-config':
        auth_name           => 'contrail-config',
        configure_user      => 'false',
        configure_user_role => 'false',
        configure_endpoint  => 'true',
        configure_service   => 'true',
        service_type        => 'sdn-l-config',
        service_description => 'Contrail configuration API',
        service_name        => 'contrail-config',
        region              => $region,
        tenant              => $tenant,
        public_url          => "${public_protocol}://${public_address}:$config_port",
        admin_url           => "${admin_protocol}://${admin_address}:$config_port",
        internal_url        => "${internal_protocol}://${internal_address}:$config_port"
    }

    # Analytics service
    $analytics_port = $contrail::analytics_port
    keystone::resource::service_identity { 'contrail-analytics':
        auth_name           => 'contrail-analytics',
        configure_user      => 'false',
        configure_user_role => 'false',
        configure_endpoint  => 'true',
        configure_service   => 'true',
        service_type        => 'sdn-l-analytics',
        service_description => 'Contrail analytics API',
        service_name        => 'contrail-analytics',
        region              => $region,
        tenant              => $tenant,
        public_url          => "${public_protocol}://${public_address}:$analytics_port",
        admin_url           => "${admin_protocol}://${admin_address}:$analytics_port",
        internal_url        => "${internal_protocol}://${internal_address}:$analytics_port",
    }
  }
}


