class contrail::provision ()
{

  run_fabric { 'prov_control_bgp': } ->
  run_fabric { 'prov_external_bgp': } ->
  run_fabric { 'prov_metadata_services': } ->
  run_fabric { 'prov_encap_type': } ->
  exec { 'add-route-target':
    path    => '/bin:/usr/bin',
    command => "python /opt/contrail/utils/add_route_target.py \
               --routing_instance_name default-domain:services:public:public \
               --router_asn ${contrail::asnum} --route_target_number 10000 \
               --api_server_ip ${contrail::contrail_mgmt_vip} --api_server_port 8082 \
               --admin_user neutron --admin_tenant_name services --admin_password ${contrail::admin_token}",
  }

  neutron_network { 'private':
    ensure      => present,
    tenant_name => 'demo',
  } ->
  neutron_subnet { 'private_subnet':
    ensure       => present,
    cidr         => $contrail::admin_tenant_private_cidr,
    network_name => 'private',
    tenant_name  => 'admin',
  }

  neutron_network { 'public':
    ensure          => present,
    shared          => 'True',
    router_external => 'True',
    tenant_name     => 'admin',
  } ->
  neutron_subnet { 'public_subnet':
    ensure       => 'present',
    cidr         =>  $contrail::admin_tenant_public_cidr,
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

