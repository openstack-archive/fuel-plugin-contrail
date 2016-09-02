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
  $tor_device_name,
  $tor_vendor_name,
  $tor_mgmt_ip,
  $tor_tun_ip,
  $ovs_protocol = 'pssl',
  $ovs_port     = $title + 9900,
  $server_names = $::contrail::tor_ips,
  $ipaddresses  = $::contrail::tor_ips,
  )
{
  if $ovs_protocol == 'pssl' {

    openstack::ha::haproxy_service { "contrail-tor-${ovs_port}":
        order                  => $order,
        listen_port            => $ovs_port,
        balancermember_port    => $ovs_port,
        server_names           => $server_names,
        ipaddresses            => $ipaddresses,
        public                 => false,
        internal               => true,
        haproxy_config_options =>
          { 'option'         => ['nolinger', 'tcp-check'],
            'balance'        => 'source',
            'mode'           => 'tcp',
            'tcp-check'      => "connect port ${ovs_port}",
            'default-server' => 'error-limit 1 on-error mark-down'
          },
        balancermember_options => 'check inter 2000 rise 2 fall 3',
      }
  }

}