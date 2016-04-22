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

class contrail::compute::vmware_nova_compute
  (
    $vcenter_hash = hiera(['vcenter']),
    $compute_vmware_clusters = vcenter_hash['computes'][0]['vc_cluster'].split(','),
    $host_ip = ,
    $host_username = ,
    $host_password = ,
{

  Package { ensure => installed }

  file {'/etc/nova/nova-compute.conf':
    content => template('contrail/nova-compute.conf.erb')

  }

}
