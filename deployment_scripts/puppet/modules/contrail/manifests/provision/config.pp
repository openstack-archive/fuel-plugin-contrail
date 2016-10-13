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

class contrail::provision::config {

  Exec {
    provider => 'shell',
    path     => '/usr/bin:/bin:/sbin',
  }

  contrail::provision::api_readiness::check{'/opt/contrail/prov_config_node-DONE':} ->
  exec { 'prov_config_node':
    command => "python /opt/contrail/utils/provision_config_node.py \
--api_server_ip ${contrail::contrail_mgmt_vip} --api_server_port ${contrail::api_server_port} \
--oper add --host_name ${::fqdn} --host_ip ${contrail::address} \
--admin_user '${contrail::neutron_user}' --admin_tenant_name '${contrail::service_tenant}' --admin_password '${contrail::service_token}' \
&& touch /opt/contrail/prov_config_node-DONE",
    creates => '/opt/contrail/prov_config_node-DONE',
  } 


  if roles_include('primary-contrail-config') {
    contrail::provision::api_readiness::check{'/opt/contrail/prov_metadata_service-DONE':} ->
    exec { 'prov_metadata_services':
      command => "python /opt/contrail/utils/provision_linklocal.py \
--api_server_ip ${contrail::contrail_mgmt_vip} --api_server_port ${contrail::api_server_port} \
--oper add \
--linklocal_service_name metadata --linklocal_service_ip 169.254.169.254 --linklocal_service_port 80 \
--ipfabric_service_ip ${contrail::mos_mgmt_vip} --ipfabric_service_port 8775  \
--admin_user '${contrail::neutron_user}' --admin_tenant_name '${contrail::service_tenant}' --admin_password '${contrail::service_token}' \
&& touch /opt/contrail/prov_metadata_service-DONE",
      creates => '/opt/contrail/prov_metadata_service-DONE',
    } ->

    contrail::provision::api_readiness::check{'/opt/contrail/prov_encap_type-DONE':} ->
    exec { 'prov_encap_type':
      command => "python /opt/contrail/utils/provision_encap.py \
--api_server_ip ${contrail::contrail_mgmt_vip} --api_server_port ${contrail::api_server_port} \
--oper add --encap_priority MPLSoUDP,MPLSoGRE,VXLAN \
--admin_user ${contrail::admin_username} --admin_password '${contrail::admin_password}' \
&& touch /opt/contrail/prov_encap_type-DONE",
      creates => '/opt/contrail/prov_encap_type-DONE',
    }
  }
}

