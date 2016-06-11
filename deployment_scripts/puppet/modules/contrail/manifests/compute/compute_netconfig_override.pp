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

class contrail::compute::compute_netconfig_override {

  if roles_include('dpdk') {
    # Override network_scheme to skip interfaces used by the vrouter
    $settings = hiera_hash('contrail', {})
    $network_scheme = hiera_hash('network_scheme')

    prepare_network_config($network_scheme)
    $override_ns = vrouter_override_network_scheme($network_scheme,
                                                  $contrail::phys_dev,
                                                  $contrail::compute_dpdk_enabled)

    file { '/etc/hiera/plugins/contrail-vrouter-override_ns.yaml':
      ensure  => file,
      content => inline_template('<%= YAML.dump @override_ns %>'),
      replace => false,
    }
  }
}
