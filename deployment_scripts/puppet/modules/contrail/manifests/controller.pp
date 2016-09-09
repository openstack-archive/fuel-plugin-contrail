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

  $custom_yaml_settings = {
    'sources' => [
      {
        'name'      => 'contrail_source',
        'interval'  => '600',
        'meters'    => [
          'ip.floating.receive.packets',
          'ip.floating.transmit.packets',
          'ip.floating.receive.bytes',
          'ip.floating.transmit.bytes',
        ],
        'resources' => ["contrail://${contrail::contrail_private_vip}:8081"],
        'sinks'     => ['contrail_sink'],
      }
    ],
    'sinks' => [
      {
        'name'         => 'contrail_sink',
        'publishers'   => ['rpc://'],
        'transformers' => '',
      }
    ]
  }

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
  if !defined(Package['neutron-server']) {
    package { 'neutron-server': }
  }
  package { 'python-neutron-lbaas':
    require => Package['neutron-server'],
  } ->
  package { 'python-contrail': } ->
  package { 'contrail-utils': } ->
  package { 'neutron-plugin-contrail': } ->
  package { 'contrail-heat': }

  # Nova configuration
  if !defined(Nova_config['DEFAULT/enabled_apis']) {
    nova_config {
      'DEFAULT/enabled_apis': value => 'ec2,osapi_compute,metadata',
    }
  }
  else {
    Nova_config<| (title == 'DEFAULT/enabled_apis') |> {
      ensure => present,
      value  => 'ec2,osapi_compute,metadata',
    }
  }
  if !defined(Nova_config['DEFAULT/firewall_driver']) {
    nova_config {
      'DEFAULT/firewall_driver': value => 'nova.virt.firewall.NoopFirewallDriver',
    }
  }
  else {
    Nova_config<| (title == 'DEFAULT/firewall_driver') |> {
      ensure => present,
      value  => 'nova.virt.firewall.NoopFirewallDriver',
    }
  }
  if !defined(Nova_config['DEFAULT/security_group_api']) {
    nova_config {
      'DEFAULT/security_group_api': value => 'neutron',
    }
  }
  else {
    Nova_config<| (title == 'DEFAULT/security_group_api') |> {
      ensure => present,
      value  => 'neutron',
    }
  }
  nova_config {
    'DEFAULT/neutron_url_timeout':            value => '300';
    'DEFAULT/service_neutron_metadata_proxy': value => 'True';
  }

  if !defined(Class['nova::api']) {
    service {'nova-api':
      ensure => running,
      enable => true,
    }
  }

  # Neutron configuration
  if !defined(Neutron_config['DEFAULT/core_plugin']) {
    neutron_config {
      'DEFAULT/core_plugin': value => 'neutron_plugin_contrail.plugins.opencontrail.contrail_plugin.NeutronPluginContrailCoreV2',
    }
  }
  else {
    Neutron_config<| (title == 'DEFAULT/core_plugin') |> {
      ensure => present,
      value  => 'neutron_plugin_contrail.plugins.opencontrail.contrail_plugin.NeutronPluginContrailCoreV2',
    }
  }
  if !defined(Neutron_config['DEFAULT/api_extensions_path']) {
    neutron_config {
      'DEFAULT/api_extensions_path': value => 'extensions:/usr/lib/python2.7/dist-packages/neutron_plugin_contrail/extensions';
    }
  }
  else {
    Neutron_config<| title == 'DEFAULT/api_extensions_path' |> {
      ensure => present,
      value  => 'extensions:/usr/lib/python2.7/dist-packages/neutron_plugin_contrail/extensions',
    }
  }
  if !defined(Neutron_config['DEFAULT/service_plugins']) {
    neutron_config {
      'DEFAULT/service_plugins': value => 'neutron_plugin_contrail.plugins.opencontrail.loadbalancer.plugin.LoadBalancerPlugin';
    }
  }
  else {
    Neutron_config<| title == 'DEFAULT/service_plugins' |> {
      ensure => present,
      value  => 'neutron_plugin_contrail.plugins.opencontrail.loadbalancer.plugin.LoadBalancerPlugin',
    }
  }
  if !defined(Neutron_config['DEFAULT/allow_overlapping_ips']) {
    neutron_config {
      'DEFAULT/allow_overlapping_ips': value => 'True';
    }
  }
  else {
    Neutron_config<| title == 'DEFAULT/allow_overlapping_ips' |> {
      ensure => present,
      value  => 'True',
    }
  }
  if !defined(Neutron_config['keystone_authtoken/auth_host']) {
    neutron_config {
      'keystone_authtoken/auth_host': value => $contrail::keystone_address;
    }
  }
  else {
    Neutron_config<| (title == 'keystone_authtoken/auth_host') |> {
      ensure => present,
      value  => $contrail::keystone_address,
    }
  }
  if !defined(Neutron_config['keystone_authtoken/auth_port']) {
    neutron_config {
      'keystone_authtoken/auth_port': value => '35357';
    }
  }
  else {
    Neutron_config<| (title == 'keystone_authtoken/auth_port')|> {
      ensure => present,
      value  => '35357',
    }
  }
  if !defined(Neutron_config['keystone_authtoken/auth_protocol']) {
    neutron_config {
      'keystone_authtoken/auth_protocol': value => $contrail::keystone_protocol;
    }
  }
  else {
    Neutron_config<| (title == 'keystone_authtoken/auth_protocol') |> {
      ensure => present,
      value  => $contrail::keystone_protocol,
    }
  }

  neutron_config {
    'service_providers/service_provider': value => 'LOADBALANCER:Opencontrail:neutron_plugin_contrail.plugins.opencontrail.loadbalancer.driver.OpencontrailLoadbalancerDriver:default';
    'QUOTAS/quota_network':               value => '-1';
    'QUOTAS/quota_subnet':                value => '-1';
    'QUOTAS/quota_port':                  value => '-1';
  } ->
  file { '/etc/contrail/vnc_api_lib.ini':
    content => template('contrail/vnc_api_lib.ini.erb')
  } ->
  contrailplugin_ini_config {
    'APISERVER/api_server_ip':       value => $contrail::contrail_mgmt_vip;
    'APISERVER/api_server_port':     value => $contrail::api_server_port;
    'APISERVER/multi_tenancy':       value => 'True';
    'APISERVER/contrail_extensions': value => 'ipam:neutron_plugin_contrail.plugins.opencontrail.contrail_plugin_ipam.NeutronPluginContrailIpam,policy:neutron_plugin_contrail.plugins.opencontrail.contrail_plugin_policy.NeutronPluginContrailPolicy,route-table:neutron_plugin_contrail.plugins.opencontrail.contrail_plugin_vpc.NeutronPluginContrailVpc,contrail:None';
    'COLLECTOR/analytics_api_ip':    value => $contrail::contrail_mgmt_vip;
    'COLLECTOR/analytics_api_port':  value => '8081';
    'KEYSTONE/auth_url':             value => $contrail::auth_url;
    'KEYSTONE/admin_token':          value => $contrail::admin_token;
    'KEYSTONE/admin_user':           value => $contrail::neutron_user;
    'KEYSTONE/admin_password':       value => $contrail::service_token;
    'KEYSTONE/admin_tenant_name':    value => $contrail::service_tenant;
  }
  if !defined(File['/etc/neutron/plugin.ini']) {
    file {'/etc/neutron/plugin.ini':
      ensure => link,
      target => '/etc/neutron/plugins/opencontrail/ContrailPlugin.ini',
    }
  }
  else {
    File <| (title == '/etc/neutron/plugin.ini') |> {
      ensure => link,
      target => '/etc/neutron/plugins/opencontrail/ContrailPlugin.ini',
    }
  }
  if !defined(Service['neutron-server']) {
    service { 'neutron-server':
      ensure    => running,
      enable    => true,
      require   => [
        Package['neutron-server'],
        Package['neutron-plugin-contrail'],
      ],
      subscribe => File['/etc/neutron/plugin.ini'],
    }
  }
  # Contrail-specific heat templates settings
  heat_config {
    'DEFAULT/plugin_dirs':            value => '/usr/lib/heat,/usr/lib/python2.7/dist-packages/contrail_heat/resources,/usr/lib/python2.7/dist-packages/vnc_api/gen/heat/resources';
    'clients_contrail/contrail-user': value => 'neutron';
    'clients_contrail/user':          value => $contrail::neutron_user;
    'clients_contrail/password':      value => $contrail::service_token;
    'clients_contrail/tenant':        value => $contrail::service_tenant;
    'clients_contrail/api_server':    value => $contrail::contrail_mgmt_vip;
    'clients_contrail/api_port':      value => $contrail::api_server_port;
    'clients_contrail/auth_host_ip':  value => $contrail::keystone_address;
    'clients_contrail/api_base_url':  value => '/';
  }
  if !defined(Service['heat-engine']) {
    service {'heat-engine':
      ensure     => running,
      name       => 'p_heat-engine',
      enable     => true,
      hasstatus  => true,
      hasrestart => true,
      provider   => 'pacemaker',
      require    => Package['contrail-heat'],
    }
  }

  # Contrail-specific ceilometer settings
  $ceilometer_enabled = $contrail::ceilometer_hash['enabled']

  if ($ceilometer_enabled) {
    package { 'ceilometer-plugin-contrail': } ->
    merge_yaml_settings { 'contrail_ceilometer_pipeline_yaml':
      ensure            => present,
      path              => '/etc/ceilometer/pipeline.yaml',
      sample_settings   => '/etc/ceilometer/pipeline.yaml',
      override_settings => $custom_yaml_settings,
      require           => Package['ceilometer-plugin-contrail'],
    }
    if $contrail::ceilometer_ha_mode {
      service {'ceilometer-agent-central':
        ensure     => running,
        name       => 'p_ceilometer-agent-central',
        enable     => true,
        hasstatus  => true,
        hasrestart => true,
        provider   => 'pacemaker',
        subscribe  => Merge_yaml_settings['contrail_ceilometer_pipeline_yaml'],
      }
    }
    else {
      if !defined(Service['ceilometer-polling']) {
        service { 'ceilometer-polling':
          ensure    => running,
          enable    => true,
          subscribe => Merge_yaml_settings['contrail_ceilometer_pipeline_yaml'],
        }
      }
      if !defined(Service['ceilometer-api']) {
        service { 'ceilometer-api':
          ensure    => running,
          enable    => true,
          subscribe => Merge_yaml_settings['contrail_ceilometer_pipeline_yaml'],
        }
      }
    }
  }
  Contrailplugin_ini_config<||> ~> File['/etc/neutron/plugin.ini']
  Heat_config<||> ~> Service['heat-engine']
  Nova_config<||> ~> Service['nova-api']
}
