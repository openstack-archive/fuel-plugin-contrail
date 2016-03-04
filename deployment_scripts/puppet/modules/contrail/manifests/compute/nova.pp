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

class contrail::compute::nova {
  nova_config {
    'DEFAULT/neutron_url':                       value => "http://${contrail::mos_mgmt_vip}:9696";
    'DEFAULT/neutron_admin_auth_url':            value => "http://${contrail::mos_mgmt_vip}:35357/v2.0/";
    'DEFAULT/network_api_class':                 value => 'nova.network.neutronv2.api.API';
    'DEFAULT/neutron_admin_tenant_name':         value => 'services';
    'DEFAULT/neutron_admin_username':            value => 'neutron';
    'DEFAULT/neutron_admin_password':            value => $contrail::service_token;
    'DEFAULT/neutron_url_timeout':               value => '300';
    'DEFAULT/firewall_driver':                   value => 'nova.virt.firewall.NoopFirewallDriver';
    'DEFAULT/security_group_api':                value => 'neutron';
    'DEFAULT/heal_instance_info_cache_interval': value => '0';
  }
  if $contrail::compute_dpdk_enabled {
    nova_config {
      'CONTRAIL/use_userspace_vhost':            value => true;
    }
  }
  if $contrail::compute_sriov_enabled {
    nova_config {
      'DEFAULT/pci_passthrough_whitelist':       value => $contrail::passthrough_whitelist;
    }
  }
  Nova_config <||> ~>
  service { 'nova-compute':
    ensure => running,
    enable => true,
  }
}
