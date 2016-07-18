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

class contrail::provision::compute {

  Exec {
    provider => 'shell',
    path     => '/bin:/sbin:/usr/bin:/usr/sbin',
  }

  package { 'contrail-utils':
    ensure => present,
  } ->
  file { '/etc/contrail/vnc_api_lib.ini':
    content => template('contrail/vnc_api_lib.ini.erb')
  } ->
  exec {'wait_for_api':
    command   => "bash -c 'if ! [[ $(curl -s -o /dev/null -w \"%{http_code}\" http://${contrail::contrail_mgmt_vip}:8082) =~ ^(200|401)$ ]];\
then exit 1; fi'",
    tries     => 10,
    try_sleep => 10,
  } ->
  file { '/opt/contrail':
    ensure => 'directory',
  }

  if $contrail::compute_dpdk_enabled {
    exec { 'provision-vrouter':
      command => "contrail-provision-vrouter \
--api_server_ip ${contrail::contrail_mgmt_vip} --api_server_port 8082 --openstack_ip ${contrail::keystone_address} \
--oper add --host_name ${::fqdn} --host_ip ${contrail::address} \
--admin_user '${contrail::neutron_user}' --admin_tenant_name '${contrail::service_tenant}' --admin_password '${contrail::service_token}' \
--dpdk_enabled \
&& touch /opt/contrail/provision-vrouter-DONE",
      creates => '/opt/contrail/provision-vrouter-DONE',
      require => File['/opt/contrail'],
    }
  }
  else {
    exec { 'provision-vrouter':
      command => "contrail-provision-vrouter \
--api_server_ip ${contrail::contrail_mgmt_vip} --api_server_port 8082 --openstack_ip ${contrail::keystone_address} \
--oper add --host_name ${::fqdn} --host_ip ${contrail::address} \
--admin_user '${contrail::neutron_user}' --admin_tenant_name '${contrail::service_tenant}' --admin_password '${contrail::service_token}' \
&& touch /opt/contrail/provision-vrouter-DONE",
      creates => '/opt/contrail/provision-vrouter-DONE',
      require => File['/opt/contrail'],
    }
  }

}
