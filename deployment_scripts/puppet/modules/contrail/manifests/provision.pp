class contrail::provision (
  $neutron_private_cidr,
  $neutron_public_cidr,
)
{
  run_fabric { 'prov_control_bgp': } ->
  run_fabric { 'prov_external_bgp': } ->
  run_fabric { 'prov_metadata_services': } ->
  run_fabric { 'prov_encap_type': }

  neutron_network { 'private':
    ensure      => present,
    tenant_name => 'demo',
  } ->
  neutron_subnet { 'private_subnet':
    ensure       => present,
    cidr         => $neutron_private_cidr,
    network_name => 'private',
    tenant_name  => 'admin',
  }

  neutron_network { 'public':
    ensure          => present,
    router_external => 'True',
    tenant_name     => 'admin',
  } ->
  neutron_subnet { 'public_subnet':
    ensure       => 'present',
    cidr         =>  $neutron_public_cidr,
    network_name => 'public',
    tenant_name  => 'admin',
  }

  neutron_router { 'admin_router':
    ensure               => present,
    tenant_name          => 'admin',
    gateway_network_name => 'public',
    require              => Neutron_subnet['public_subnet'],
  } ->
  neutron_router_interface { 'admin_router:private_subnet':
    ensure  => present,
    require => Neutron_subnet['private_subnet'],
  }

}

