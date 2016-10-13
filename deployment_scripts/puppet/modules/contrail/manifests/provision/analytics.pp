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

class contrail::provision::analytics {

  Exec {
    provider => 'shell',
    path     => '/usr/bin:/bin:/sbin',
  }

contrail::provision::api_readiness::check{'/opt/contrail/prov_analytics_node-DONE':} ->
  exec { 'prov_analytics_node':
    command => "python /opt/contrail/utils/provision_analytics_node.py \
--api_server_ip ${contrail::contrail_mgmt_vip} --api_server_port ${contrail::api_server_port} \
--oper add --host_name ${::fqdn} --host_ip ${contrail::address} \
--admin_user '${contrail::neutron_user}' --admin_tenant_name '${contrail::service_tenant}' --admin_password '${contrail::service_token}' \
&& touch /opt/contrail/prov_analytics_node-DONE",
    creates => '/opt/contrail/prov_analytics_node-DONE',
  }
}
