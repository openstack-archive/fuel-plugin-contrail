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

class contrail::controller::aggregate {

  if $contrail::global_dpdk_enabled {

    $nodes_hash          = hiera('nodes')
    $dpdk_compute_nodes  = nodes_with_roles($nodes_hash, ['dpdk'], 'fqdn')
    $dpdk_hosts          = join($dpdk_compute_nodes, ',')
    $nova_hash           = hiera_hash('nova', {})
    $keystone_tenant     = pick($nova_hash['tenant'], 'services')
    $keystone_user       = pick($nova_hash['user'], 'nova')
    $service_endpoint    = hiera('service_endpoint')
    $region              = hiera('region', 'RegionOne')

    Exec {
      provider => 'shell',
      path => '/sbin:/usr/sbin:/bin:/usr/bin',
      environment => [
        "OS_TENANT_NAME=${keystone_tenant}",
        "OS_USERNAME=${keystone_user}",
        "OS_PASSWORD=${nova_hash['user_password']}",
        "OS_AUTH_URL=http://${service_endpoint}:5000/v2.0/",
        'OS_ENDPOINT_TYPE=internalURL',
        "OS_REGION_NAME=${region}",
        'NOVA_ENDPOINT_TYPE=internalURL',
      ],
    }

    nova_aggregate { 'hpgs-aggr':
      ensure            => present,
      availability_zone => 'hpgs',
      metadata          => 'hpgs=true',
      hosts             => $dpdk_hosts,
    } ->
    exec { 'create-m1.small.hpgs-flavor' :
      command   => 'bash -c "nova flavor-create --is-public true m1.small.hpgs auto 512 0 2"',
      unless    => 'bash -c "nova flavor-list | grep -q m1.small.hpgs"',
      tries     => 10,
      try_sleep => 2,
    } ->
    exec { 'create-m1.small.hpgs-mempage' :
      command   => 'bash -c "nova flavor-key m1.small.hpgs set hw:mem_page_size=large"',
      tries     => 10,
      try_sleep => 2,
    } ->
    exec { 'create-m1.small.hpgs-aggregate' :
      command   => 'bash -c "nova flavor-key m1.small.hpgs set aggregate_instance_extra_specs:hpgs=true"',
      tries     => 10,
      try_sleep => 2,
    }
  }
}
