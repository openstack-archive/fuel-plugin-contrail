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

class contrail::service ( $node_role ) {

  case $node_role {
    'controller','primary-controller': {
      $services = $operatingsystem ? {
        'Ubuntu' => ['nova-api','nova-scheduler','nova-conductor','heat-api','heat-api-cfn','heat-engine'],
        'CentOS' => ['openstack-nova-api','openstack-nova-scheduler','openstack-nova-conductor',
                    'openstack-heat-api','openstack-heat-api-cfn','openstack-heat-engine'],
        default  => undef,
      }
      notify { 'restart-services':
        notify => Service[$services],
      }
    }
  }

  if ( $services ) {
    service { $services:
      ensure => running,
      enable => true,
    }
  }

}
