class contrail::provision ( $node_role ) {

  case $node_role {
    'base-os': {
      run_fabric { 'prov_control_bgp': } ->
      run_fabric { 'prov_external_bgp': } ->
      run_fabric { 'prov_metadata_services': } ->
      run_fabric { 'prov_encap_type': }
    }
    'compute': {
      exec { 'provision-vrouter':
        path    => '/bin:/usr/bin/',
        command => "python /opt/contrail/utils/provision_vrouter.py --host_name ${::hostname} \
--host_ip ${contrail::address} --api_server_ip ${contrail::contrail_mgmt_vip} --openstack_ip ${contrail::mos_mgmt_vip} \
--admin_user neutron --admin_password ${contrail::admin_token} --admin_tenant_name services --oper add",
      }
    }
  }

}

