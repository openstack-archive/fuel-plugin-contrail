#    Copyright 2016 Mirantis, Inc.
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

class contrail::compute::vmware {

  nova_config {
    'DEFAULT/network_api_class':                 value => 'nova.network.neutronv2.api.API';
    'DEFAULT/security_group_api':                value => 'neutron';
    'DEFAULT/firewall_driver':                   value => 'nova.virt.firewall.NoopFirewallDriver';
    'DEFAULT/heal_instance_info_cache_interval': value => '0';
    'neutron/url':                               value => "${contrail::internal_neutron_protocol}://${contrail::internal_neutron_endpoint}:9696";
    'neutron/url_timeout':                       value => '300';
    'neutron/admin_auth_url':                    value => "${contrail::internal_auth_protocol}://${contrail::internal_auth_address}:35357/v2.0/";
    'neutron/admin_tenant_name':                 value => 'services';
    'neutron/admin_username':                    value => 'neutron';
    'neutron/admin_password':                    value => $contrail::service_token;
  }

  # Config file
  file { ['/etc/contrail', '/var/log/contrail']:
    ensure => directory,
    mode   => '0750',
  }
  file { 'vrouter_to_esxi_map' :
    ensure  => present,
    owner   => 'root',
    group   => 'root',
    mode    => '0755',
    content => template('contrail/vrouter_to_esxi_map.py.erb'),
    path    => '/usr/local/bin/vrouter_to_esxi_map',
  }
  vcenter_vrouter_map { 'ESXiToVRouterIp.map' :
    ensure       => present,
    password     => $contrail::vcenter_server_pass,
    username     => $contrail::vcenter_server_user,
    vcenter_host => $contrail::vcenter_server_ip,
    ips          => $contrail::contrail_vcenter_vm_ips,
    path         => '/etc/contrail/ESXiToVRouterIp.map',
    yaml         => false,
  }

  contrail_vcenter_plugin_config {
    'DEFAULT/vcenter.url':          value => "https://${contrail::vcenter_server_ip}/sdk";
    'DEFAULT/vcenter.username':     value => $contrail::vcenter_server_user;
    'DEFAULT/vcenter.password':     value => $contrail::vcenter_server_pass;
    'DEFAULT/vcenter.datacenter':   value => $contrail::contrail_vcenter_datacenter;
    'DEFAULT/vcenter.dvswitch':     value => $contrail::contrail_vcenter_dvswitch;
    'DEFAULT/vcenter.ipfabricpg':   value => $contrail::contrail_vcenter_prv_vswitchpg;
    'DEFAULT/mode':                 value => 'vcenter-as-compute';
    'DEFAULT/auth_url':             value => "${contrail::internal_auth_protocol}://${contrail::internal_auth_address}:35357/v2.0";
    'DEFAULT/admin_user':           value => $contrail::neutron_user;
    'DEFAULT/admin_password':       value => $contrail::service_token;
    'DEFAULT/admin_tenant_name':    value => $contrail::service_tenant;
    'DEFAULT/api.hostname':         value => $contrail::contrail_private_vip;
    'DEFAULT/api.port':             value => $contrail::api_server_port;
    'DEFAULT/zookeeper.serverlist': value => $contrail::zk_server_ip;
    'DEFAULT/introspect.port':      value => '8234';
  }

  service { 'contrail-vcenter-plugin':
    ensure => running,
    enable => true,
  }
  service { 'nova-compute':
    ensure => running,
    enable => true,
  }

  File['vrouter_to_esxi_map']                ~> Vcenter_vrouter_map['ESXiToVRouterIp.map']
  Nova_Config <||>                           ~> Service['nova-compute']
  Vcenter_vrouter_map['ESXiToVRouterIp.map'] ~> Service['contrail-vcenter-plugin']
  Contrail_vcenter_plugin_config <||>        ~> Service['contrail-vcenter-plugin']

}


