class contrail::config ( $node_role ) {
  case $node_role {
  'controller','primary_controller': {
    nova_config {
      'DEFAULT/network_api_class': value=> 'nova.network.neutronv2.api.API';
      'DEFAULT/neutron_url': value => "http://${contrail::public_last}:9696";
      'DEFAULT/neutron_admin_tenant_name': value=> 'services';
      'DEFAULT/neutron_admin_username': value=> 'neutron';
      'DEFAULT/neutron_admin_password': value=> "${contrail::keystone['admin_token']}";
      'DEFAULT/neutron_url_timeout': value=> '300';
      'DEFAULT/neutron_admin_auth_url': value=> "http://${contrail::mos_mgmt_vip}:35357/v2.0/";
      'DEFAULT/firewall_driver': value=> 'nova.virt.firewall.NoopFirewallDriver';
      'DEFAULT/enabled_apis': value=> 'ec2;osapi_compute;metadata';
      'DEFAULT/security_group_api': value=> 'neutron';
      'DEFAULT/service_neutron_metadata_proxy': value=> 'True';
    }
  }
}