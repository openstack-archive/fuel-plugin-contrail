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
class contrail::tsn () {

if $::contrail::enable_tor_agents == true {

  if $::contrail::tor_agents_ssl == false {
    $default_ovs_protocol = 'tcp'
  } else {
    $default_ovs_protocol = 'pssl'
  }
  package {'openvswitch-common':
      ensure => present
  }

  exec { 'generate_ca_cert':
    provider => 'shell',
    path     => '/usr/bin:/bin:/sbin',
    command  => 'ovs-pki init --force',
    creates  => '/var/lib/openvswitch/pki/switchca/cacert.pem',
    require  => Package['openvswitch-common'],
  }

  if $::contrail::tor_agents_ssl {
    exec { "generate_tor-agent_cert":
      provider => 'shell',
      path     => '/usr/bin:/bin:/sbin',
      cwd      => '/etc/contrail/',
      command  => "ovs-pki req+sign tor-${name}",
      creates  => "/etc/contrail/tor-${name}-cert.pem",
      require  => Exec['generate_ca_cert'],
    }
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
    'notify'       => 'Service[supervisor-vrouter]',
    'ovs_protocol' => $default_ovs_protocol,
  }

  create_resources(::contrail::tor_agent, $::contrail::tor_agents_configurations, $tor_agents_defaults)
  create_resources(::contrail::provision::tor_agent, $::contrail::tor_agents_configurations)
}


}
