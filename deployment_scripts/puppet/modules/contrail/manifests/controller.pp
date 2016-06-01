#    Copyright 2015 Mirantis, Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

class contrail::controller {

# Resources defaults
  Package { ensure => present }

  File {
    ensure  => present,
    mode    => '0644',
    owner   => root,
    group   => root,
    require => Package['neutron-plugin-contrail'],
  }

# Packages
  package { 'neutron-server': } ->
  package { 'python-neutron-lbaas': } ->
  package { 'python-contrail': } ->
  package { 'contrail-utils': } ->
  package { 'neutron-plugin-contrail': } ->
  package { 'contrail-heat': }


#Fix for certifi CA blocking self signed certificates
  if $contrail::public_ssl {
    file{'/usr/lib/python2.7/dist-packages/certifi/cacert.pem':
      ensure  => 'link',
      target  => '/etc/ssl/certs/ca-certificates.crt',
      require => Package['python-contrail']
    }
  }

# Nova configuration
  nova_config {
    'DEFAULT/network_api_class': value=> 'nova.network.neutronv2.api.API';
    'DEFAULT/neutron_url': value => "http://${contrail::mos_mgmt_vip}:9696";
    'DEFAULT/neutron_url_timeout': value=> '300';
    'DEFAULT/neutron_admin_auth_url': value=> "http://${contrail::mos_mgmt_vip}:35357/v2.0";
    'DEFAULT/firewall_driver': value=> 'nova.virt.firewall.NoopFirewallDriver';
    'DEFAULT/enabled_apis': value=> 'ec2,osapi_compute,metadata';
    'DEFAULT/security_group_api': value=> 'neutron';
    'DEFAULT/service_neutron_metadata_proxy': value=> 'True';
  } ~>
  service {'nova-api':
    ensure => running,
    enable => true,
  }

# Neutron configuration
  neutron_config {
    'DEFAULT/core_plugin': value => 'neutron_plugin_contrail.plugins.opencontrail.contrail_plugin.NeutronPluginContrailCoreV2';
    'DEFAULT/api_extensions_path': value => 'extensions:/usr/lib/python2.7/dist-packages/neutron_plugin_contrail/extensions';
    'DEFAULT/service_plugins': value => 'neutron_plugin_contrail.plugins.opencontrail.loadbalancer.plugin.LoadBalancerPlugin';
    'DEFAULT/allow_overlapping_ips': value => 'True';
    'service_providers/service_provider': value => 'LOADBALANCER:Opencontrail:neutron_plugin_contrail.plugins.opencontrail.loadbalancer.driver.OpencontrailLoadbalancerDriver:default';
    'keystone_authtoken/auth_host': value => $contrail::mos_mgmt_vip;
    'keystone_authtoken/auth_port': value => '35357';
    'keystone_authtoken/auth_protocol': value => 'http';
    'QUOTAS/quota_network': value => '-1';
    'QUOTAS/quota_subnet': value => '-1';
    'QUOTAS/quota_port': value => '-1';
  } ->
  file {'/etc/neutron/plugins/opencontrail/ContrailPlugin.ini':
    content => template('contrail/ContrailPlugin.ini.erb'),
  } ->
  file {'/etc/neutron/plugin.ini':
    ensure => link,
    target => '/etc/neutron/plugins/opencontrail/ContrailPlugin.ini'
  }

# Contrail-specific heat templates settings
  heat_config {
    'DEFAULT/plugin_dirs': value => '/usr/lib/heat,/usr/lib/python2.7/dist-packages/contrail_heat';
    'clients_contrail/contrail-user': value=> 'neutron';
    'clients_contrail/user': value=> 'neutron';
    'clients_contrail/password': value=> $contrail::service_token;
    'clients_contrail/tenant': value=> 'services';
    'clients_contrail/api_server': value=> $contrail::contrail_mgmt_vip;
    'clients_contrail/auth_host_ip': value=> $contrail::mos_mgmt_vip;
    'clients_contrail/api_base_url': value=> '/';
  } ~>
  service {'heat-engine':
    ensure     => running,
    name       => 'p_heat-engine',
    enable     => true,
    hasstatus  => true,
    hasrestart => true,
    provider   => 'pacemaker',
    require    => Package['contrail-heat'],
  }

# Contrail-specific ceilometer settings
  $ceilometer_enabled = $contrail::ceilometer_hash['enabled']

  if ($ceilometer_enabled) {
    package { 'ceilometer-plugin-contrail': } ->
    file {'/etc/ceilometer/pipeline.yaml':
      ensure  => file,
      content => template('contrail/pipeline.yaml.erb'),
    } ~>
    service {'ceilometer-agent-central':
      ensure     => running,
      name       => 'p_ceilometer-agent-central',
      enable     => true,
      hasstatus  => true,
      hasrestart => true,
      provider   => 'pacemaker',
    }
  }

  Neutron_config <||> ~>
  service { 'neutron-server':
    ensure    => running,
    enable    => true,
    subscribe => [Package['neutron-server'],Package['neutron-plugin-contrail'],
                  File['/etc/neutron/plugins/opencontrail/ContrailPlugin.ini'],
                  File['/etc/neutron/plugin.ini'],
                  ],
  }

}
