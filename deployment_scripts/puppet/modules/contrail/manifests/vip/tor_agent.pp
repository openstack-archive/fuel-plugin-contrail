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

define contrail::vip::tor_agent (
  $order,
  $ovs_protocol,
  $ovs_port     = 9900 + $title,
  $listen_port  = $ovs_port,
  $balance_port = $listen_port,
  $server_names = $::contrail::tor_ips,
  $ipaddresses  = $::contrail::tor_ips,
  )
{
  if $ovs_protocol == 'pssl' {

    openstack::ha::haproxy_service { "contrail-tor-${name}-${listen_port}":
        order                  => $order,
        listen_port            => $listen_port,
        balancermember_port    => $balance_port,
        server_names           => $server_names,
        ipaddresses            => $ipaddresses,
        public                 => false,
        internal               => true,
        haproxy_config_options => { 'option'  => ['tcplog', 'redispatch','tcpka'],
                                    'balance' => 'roundrobin',
                                    'timeout' => ['connect 5000', 'client 24h', 'server 24h'],
                                    'mode'    => 'tcp',
                                    'retries' => '3' },
        balancermember_options => 'check inter 10s fastinter 2s downinter 3s rise 3 fall 3',
      }
  }

}