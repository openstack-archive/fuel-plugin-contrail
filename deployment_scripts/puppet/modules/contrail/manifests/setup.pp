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

class contrail::setup ($node_name)
{
  if $node_name == $contrail::deployment_node {

    $pythonpath = $operatingsystem ? {
      'Ubuntu' => '/usr/local/lib/python2.7/dist-packages',
      'CentOS' => '/usr/lib/python2.6/site-packages'
    }
    file {'/tmp/install.py.patch':
      ensure => file,
      source => 'puppet:///modules/contrail/install.py.patch'
    } ->
    exec {'install.py.patch':
    command => 'patch /opt/contrail/utils/fabfile/tasks/install.py /tmp/install.py.patch && touch /opt/contrail/install.py.patch-DONE',
    creates => '/opt/contrail/install.py.patch-DONE'
    } ->
    file {'/tmp/commandline.py.patch':
      ensure => file,
      source => 'puppet:///modules/contrail/commandline.py.patch'
    } ->
    exec {'commandline.py.patch':
    command => 'patch /opt/contrail/utils/fabfile/utils/commandline.py /tmp/commandline.py.patch && touch /opt/contrail/commandline.py.patch-DONE',
    creates => '/opt/contrail/commandline.py.patch-DONE'
    } ->

    # Database installation
    #run_fabric { 'install_database': } ->
    #run_fabric { 'setup_database': } ->
    notify{"Waiting for cassandra nodes: ${contrail::contrail_node_num}":} ->
    exec {'wait_for_cassandra':
      provider  => 'shell',
      command   => "if [ `nodetool status|grep ^UN|wc -l` -lt ${contrail::contrail_node_num} ]; then exit 1; fi",
      tries     => 10, # wait for whole cluster is up: 10 tries every 30 seconds = 5 min
      try_sleep => 30,
    } ->
    # Installing components
    #run_fabric { 'install_cfgm': } ->
    #run_fabric { 'install_control': } ->
    #run_fabric { 'install_collector': } ->
    run_fabric { 'install_webui': } ->
    # Some fixups
    #run_fabric { 'setup_contrail_keepalived': } ->
    #run_fabric { 'fixup_restart_haproxy_in_collector': } ->
    run_fabric { 'fix-service-tenant-name':
      hostgroup => 'control',
      command   => "sed -i '49s/service/services/g' ${pythonpath}/contrail_provisioning/config/quantum_in_keystone_setup.py",
    } ->
    # Setting up the components
    #run_fabric { 'setup_cfgm': } ->
    exec {'update_neutron_pwd':
      command => "keystone --os-endpoint http://${contrail::mos_mgmt_vip}:35357/v2.0 --os-token ${contrail::admin_token} \
--os-tenant-name services user-password-update --pass  ${contrail::service_token}  neutron"} ->
    #run_fabric { 'setup_control': } ->
    #run_fabric { 'setup_collector': } ->
    run_fabric { 'setup_webui': }

  }

}
