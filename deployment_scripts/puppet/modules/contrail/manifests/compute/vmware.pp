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

class contrail::compute::vmware {

  nova_config {
    'neutron/auth_type':    value => 'password';
    'neutron/auth_url':     value => "http://${contrail::mos_mgmt_vip}:35357/";
    'neutron/username':     value => 'neutron';
    'neutron/password':     value => $contrail::service_token;
    'neutron/project_name': value => 'services';
    'neutron/url':          value => "http://${contrail::mos_mgmt_vip}:9696";
  }

  ini_setting { 'vmware-int-dvs':
    ensure  => present,
    path    => '/etc/nova/nova-compute.conf',
    section => 'vmware',
    setting => 'vcenter_dvswitch',
    value   => $contrail::dvs_internal,
  }

  # Config file
  file { '/etc/contrail':
    ensure => directory,
    mode   => '0750',
  }->
  file { '/var/log/contrail':
    ensure => directory,
    mode   => '0750',
  }->
  file {'/etc/contrail/ESXiToVRouterIp.map':
    content => template('contrail/ESXiToVRouterIp.map.erb')
  }->
  file {'/etc/contrail/contrail-vcenter-plugin.conf':
    ensure  => present,
    content => template('contrail/contrail-vcenter-plugin.conf.erb'),
  }~>
  # Enable and start service
  service { 'contrail-vcenter-plugin':
    ensure => running,
    enable => true,
  }

  Ini_setting['vmware-int-dvs'] ->
  Nova_Config <||> ~>
  service { 'nova-compute':
    ensure => running,
    enable => true,
  }

}
