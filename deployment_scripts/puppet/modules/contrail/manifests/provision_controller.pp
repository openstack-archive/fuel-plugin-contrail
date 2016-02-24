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

class contrail::provision_controller {

contrail::create_network{'net04':
  netdata          => $contrail::nets['net04'],
} ->

contrail::create_network{'net04_ext':
  netdata => $contrail::nets['net04_ext'],
  notify  => Exec['prov_route_target'],
} ->

openstack::network::create_router{'router04':
  internal_network => 'net04',
  external_network => 'net04_ext',
  tenant_name      => $contrail::admin_tenant
}

exec { 'prov_route_target':
  provider => 'shell',
  path     => '/usr/bin:/bin:/sbin',
  command  => "python /usr/share/contrail-utils/add_route_target.py \
--routing_instance_name default-domain:${contrail::admin_tenant}:net04_ext:net04_ext \
--route_target_number ${contrail::route_target} --router_asn ${contrail::asnum} \
--api_server_ip ${contrail::contrail_mgmt_vip} --api_server_port 8082 \
--admin_user neutron --admin_tenant_name services --admin_password '${contrail::service_token}' \
&& touch /etc/contrail/prov_route_target-DONE",
  creates  => '/etc/contrail/prov_route_target-DONE',
  require  => Contrail::Create_Network['net04_ext'],
}

}
