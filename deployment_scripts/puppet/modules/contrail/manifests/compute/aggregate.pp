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

class contrail::compute::aggregate {

  if $contrail::compute_dpdk_enabled {

    $nodes_hash             = hiera('nodes')
    $dpdk_compute_nodes     = nodes_with_roles(['dpdk'], 'fqdn')
    $dpdk_hosts             = join($dpdk_compute_nodes, ',')
    $nova_hash              = hiera_hash('nova', {})
    $keystone_tenant        = pick($nova_hash['tenant'], 'services')
    $keystone_user          = pick($nova_hash['user'], 'nova')
    $service_endpoint       = hiera('service_endpoint')
    $region                 = hiera('region', 'RegionOne')
    $ssl_hash               = hiera_hash('use_ssl', {})
    $internal_auth_protocol = get_ssl_property($ssl_hash, {}, 'keystone', 'internal', 'protocol', 'http')
    $internal_auth_address  = get_ssl_property($ssl_hash, {}, 'keystone', 'internal', 'hostname', [$service_endpoint])
    $auth_api_version       = 'v2.0'
    $identity_uri           = "${internal_auth_protocol}://${internal_auth_address}:5000"
    $auth_url               = "${identity_uri}/${auth_api_version}"

    Exec {
      provider    => 'shell',
      path        => '/sbin:/usr/sbin:/bin:/usr/bin',
      tries       => 10,
      try_sleep   => 2,
      environment => [
        "OS_TENANT_NAME=${keystone_tenant}",
        "OS_USERNAME=${keystone_user}",
        "OS_PASSWORD=${nova_hash['user_password']}",
        "OS_AUTH_URL=${auth_url}",
        'OS_ENDPOINT_TYPE=internalURL',
        "OS_REGION_NAME=${region}",
        'NOVA_ENDPOINT_TYPE=internalURL',
      ],
    }

    exec { 'aggr_add_host':
      command => "bash -c \"nova aggregate-add-host hpgs-aggr ${::fqdn}\" && touch /opt/contrail/aggr_add_host-DONE",
      creates => '/opt/contrail/aggr_add_host-DONE',
    }
  }
}

