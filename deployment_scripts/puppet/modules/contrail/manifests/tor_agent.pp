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
define contrail::tor_agent (
  $ovs_port,
  $contrail_dev_ip           = $::contrail::address,
  $tsn_vip_ip                = '127.0.0.1',
  $tor_id                    = $name,
  $ovs_protocol,
  $contrail_discovery_server = $::contrail::contrail_private_vip,
)
{

  file{"/etc/contrail/contrail-tor-agent-${name}.conf":
    content => template('contrail-tor-agent.conf.erb')
  } ->

  file{"/etc/contrail/supervisor_vrouter_files/contrail-tor-agent-${name}.ini":
    content => template('contrail-tor-agent.ini.erb')
  } ->

  ::contrail::provision::tor_agent{ $name:
    tor_id => $tor_id
  }

}
