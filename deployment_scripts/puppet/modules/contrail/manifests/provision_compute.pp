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

class contrail::provision_compute {

  Exec {
    provider => 'shell',
    path     => '/bin:/sbin:/usr/bin:/usr/sbin',
  }

  package { 'contrail-utils':
    ensure => present,
  } ->
  exec { 'provision-vrouter':
    command => "contrail-provision-vrouter \
--api_server_ip ${contrail::contrail_mgmt_vip} --api_server_port 8082 --openstack_ip ${contrail::mos_mgmt_vip} \
--oper add --host_name ${::fqdn} --host_ip ${contrail::address} \
--admin_user neutron --admin_tenant_name services --admin_password ${contrail::service_token} \
&& touch /opt/contrail/provision-vrouter-DONE",
    creates => '/opt/contrail/provision-vrouter-DONE',
  }

  exec {'no_network_reconfigure':
    command => 'echo "#NOOP here. Modified by contrail plugin" > /etc/puppet/modules/osnailyfacter/modular/netconfig/netconfig.pp',
    require => Exec['provision-vrouter'],
  }

  exec {'no_openstack_network_reconfigure':
    command => 'echo "#NOOP here. Modified by contrail plugin" > /etc/puppet/modules/osnailyfacter/modular/openstack-network/openstack-network-compute.pp',
    require => Exec['provision-vrouter'],
  }

}
