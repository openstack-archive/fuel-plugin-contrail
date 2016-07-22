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

class contrail::provision::controller {

  if $::contrail::settings['provision_networks'] {

    contrail::create_network{$contrail::private_net:
      netdata     => $contrail::nets[$contrail::private_net],
      tenant_name => $contrail::admin_tenant,
    } ->

    contrail::create_network{$contrail::floating_net:
      netdata     => $contrail::nets[$contrail::floating_net],
      notify      => Exec['prov_route_target'],
      tenant_name => $contrail::admin_tenant,
    } ->

    neutron_router { $contrail::default_router:
      ensure               => 'present',
      gateway_network_name => $contrail::floating_net,
      name                 => $contrail::default_router,
      tenant_name          => $contrail::admin_tenant,
    } ->

    neutron_router_interface { "${contrail::default_router}:${contrail::private_net}__subnet":
      ensure => 'present',
    }

    exec { 'prov_route_target':
      provider => 'shell',
      path     => '/usr/bin:/bin:/sbin',
      command  => "python /usr/share/contrail-utils/add_route_target.py \
    --routing_instance_name default-domain:${contrail::admin_tenant}:${contrail::floating_net}:${contrail::floating_net} \
    --route_target_number ${contrail::route_target} --router_asn ${contrail::asnum} \
    --api_server_ip ${contrail::contrail_mgmt_vip} --api_server_port 8082 \
    --admin_user '${contrail::neutron_user}' --admin_tenant_name '${contrail::service_tenant}' --admin_password '${contrail::service_token}' \
    && touch /etc/contrail/prov_route_target-DONE",
      creates  => '/etc/contrail/prov_route_target-DONE',
      require  => Contrail::Create_Network[$contrail::floating_net],
    }

  }

}
