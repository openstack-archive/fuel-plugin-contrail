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

class contrail::provision::db {

  Exec {
    provider => 'shell',
    path     => '/usr/bin:/bin:/sbin',
  }

# VNC config for provision scripts
  file { '/etc/contrail/vnc_api_lib.ini':
    content => template('contrail/vnc_api_lib.ini.erb')
  }

  notify {'Waiting for contrail API':} ->

  exec {'wait_for_api':
    command   => "if [ `curl --silent --output /dev/null --write-out \"%{http_code}\" http://${contrail::contrail_mgmt_vip}:8082` -lt 401 ];\
then exit 1; fi",
    tries     => 10,
    try_sleep => 10,
  } ->

  exec { 'prov_database_node':
    command => "python /opt/contrail/utils/provision_database_node.py \
--api_server_ip ${contrail::contrail_mgmt_vip} --api_server_port 8082 \
--oper add --host_name ${::fqdn} --host_ip ${contrail::address} \
--admin_user neutron --admin_tenant_name services --admin_password ${contrail::service_token} \
&& touch /opt/contrail/prov_database_node-DONE",
    creates => '/opt/contrail/prov_database_node-DONE',
  }

}

