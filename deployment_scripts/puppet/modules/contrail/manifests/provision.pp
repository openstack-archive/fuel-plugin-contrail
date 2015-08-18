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

class contrail::provision ( $node_role ) {

  case $node_role {
    'base-os': {
      run_fabric { 'prov_control_bgp': } ->
      run_fabric { 'prov_external_bgp': } ->
      run_fabric { 'prov_metadata_services': } ->
      run_fabric { 'prov_encap_type': }
    }
    'controller','primary-controller': {
      keystone_endpoint {'RegionOne/neutron':
        ensure       => present,
        public_url   => "http://${contrail::contrail_mgmt_vip}:9696/",
        admin_url    => "http://${contrail::contrail_mgmt_vip}:9696/",
        internal_url => "http://${contrail::contrail_mgmt_vip}:9696/",
      }
    }
    'compute': {
      exec { 'provision-vrouter':
        path    => '/bin:/usr/bin/',
        command => "python /opt/contrail/utils/provision_vrouter.py --host_name ${::fqdn} \
--host_ip ${contrail::address} --api_server_ip ${contrail::contrail_mgmt_vip} --openstack_ip ${contrail::mos_mgmt_vip} \
--admin_user neutron --admin_password ${contrail::service_token} --admin_tenant_name services --oper add && touch /opt/contrail/provision-vrouter-DONE",
        creates => '/opt/contrail/provision-vrouter-DONE',
      }
    }
    default: {}
  }

}

