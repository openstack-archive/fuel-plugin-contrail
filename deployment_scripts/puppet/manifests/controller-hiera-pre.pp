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

notice('MODULAR: contrail/controller-hiera-pre.pp')

include contrail

$hiera_dir = '/etc/hiera/override'
$plugin_name = 'contrail'
$plugin_yaml = "${plugin_name}.yaml"

$contrail_plugin = hiera('contrail', undef)

file_line {"${plugin_name}_hiera_override":
  path  => '/etc/hiera.yaml',
  line  => "  - override/${plugin_name}",
  after => '  - override/module/%{calling_module}',
}

file {'/etc/hiera/override':
  ensure  => directory,
} ->
# Pre-deploy
# Empty predefined_networks to skip OSTF nets creation
# in openstack-network-controller.pp
file { "${hiera_dir}/${plugin_yaml}":
  ensure  => file,
  content => 'quantum_settings: { neutron_agents: [], predefined_networks: [] }',
}

if $contrail::use_vcenter {
  file { '/root/config-override.yaml':
    ensure  => file,
    content => inline_template("<%= scope.lookupvar('contrail::vcenter_hash').to_yaml.gsub('---','vcenter:') %>"),
  }

  contrail::deliver_hiera {$contrail::contrail_config_ips_adm:}
}
