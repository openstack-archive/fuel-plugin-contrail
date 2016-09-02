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
class contrail::tsn (
  $ovs_protocol = 'pssl'
  ) {

if $::contrail::enable_tor_agents == true {

  package {'openvswitch-common':
      ensure => present
  }

  service {'nova-compute':
    ensure => stopped
  } ->

  ini_setting {'set_tsn_vrouter':
    ensure  => present,
    path    => '/etc/contrail/contrail-vrouter-agent.conf',
    section => 'DEFAULT',
    setting => 'agent_mode',
    value   => 'tsn',
  } ~>

  service {'supervisor-vrouter':
    ensure => 'running'
  }

  $tor_agents_defaults = {
    'notify'       => 'Service[supervisor-vrouter]'
  }

  create_resources(::contrail::tor_agent, $::contrail::tor_agents_configurations, $tor_agents_defaults)
  create_resources(::contrail::provision::tor_agent, $::contrail::tor_agents_configurations)
}


}
