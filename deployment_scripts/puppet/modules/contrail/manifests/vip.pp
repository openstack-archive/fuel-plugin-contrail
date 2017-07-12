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

class contrail::vip {

  if $contrail::public_ssl {
    $ui_backend_port = 8080
    $mode = 'http'
  } else {
    $ui_backend_port = 8143
    $mode = 'tcp'
  }

  Openstack::Ha::Haproxy_service {
    internal_virtual_ip => $contrail::contrail_private_vip,
    public_virtual_ip   => $contrail::mos_public_vip,
  }

  openstack::ha::haproxy_service { 'contrail-analytics-api':
    order                  => '201',
    listen_port            => 8081,
    balancermember_port    => 9081,
    server_names           => $contrail::contrail_analytics_ips,
    ipaddresses            => $contrail::contrail_analytics_ips,
    public                 => true,
    internal               => true,
    public_ssl             => $contrail::public_ssl,
    public_ssl_path        => $contrail::public_ssl_path,
    haproxy_config_options => { 'option'         => ['nolinger', 'tcp-check', 'httplog'],
                                'balance'        => 'roundrobin',
                                'default-server' => 'error-limit 1 on-error mark-down',
                                'http-request'   => 'add-header X-Forwarded-Proto https if { ssl_fc }',
    },
    balancermember_options => 'check inter 2000 rise 2 fall 3',
  }

  openstack::ha::haproxy_service { 'contrail-configuration-api':
    order                  => '202',
    listen_port            => $contrail::api_server_port,
    balancermember_port    => 9100,
    server_names           => $contrail::contrail_config_ips,
    ipaddresses            => $contrail::contrail_config_ips,
    public                 => true,
    internal               => true,
    public_ssl             => $contrail::public_ssl,
    public_ssl_path        => $contrail::public_ssl_path,
    haproxy_config_options => { 'option'         => ['nolinger', 'httplog'],
                                'balance'        => 'roundrobin',
                                'http-request'   => 'add-header X-Forwarded-Proto https if { ssl_fc }',
                                'timeout'        => ['server 3m', 'client 3m'] },
    balancermember_options => 'check inter 2000 rise 2 fall 3',
  }

  openstack::ha::haproxy_service { 'contrail-discovery':
    order                  => '203',
    listen_port            => 5998,
    balancermember_port    => 9110,
    server_names           => $contrail::contrail_config_ips,
    ipaddresses            => $contrail::contrail_config_ips,
    public                 => false,
    internal               => true,
    haproxy_config_options => { 'option'  => ['nolinger', 'httplog'],
                                'balance' => 'roundrobin' },
    balancermember_options => 'check inter 2000 rise 2 fall 3',
  }

  openstack::ha::haproxy_service { 'contrail-webui':
    order                  => '204',
    listen_port            => 8143,
    balancermember_port    => $ui_backend_port,
    server_names           => $contrail::contrail_config_ips,
    ipaddresses            => $contrail::contrail_config_ips,
    public                 => true,
    internal               => false,
    public_ssl             => $contrail::public_ssl,
    public_ssl_path        => $contrail::public_ssl_path,
    haproxy_config_options => { 'option'         => ['nolinger', 'tcp-check', 'httplog'],
                                'balance'        => 'source',
                                'rspirep'        => '^(set-cookie:.*)  \1;\ Secure',
                                'default-server' => 'error-limit 1 on-error mark-down',
                                'mode'           => $mode,
                                'http-request'   => 'add-header X-Forwarded-Proto https if { ssl_fc }'},
    balancermember_options => 'check inter 2000 rise 2 fall 3',
  }

  openstack::ha::haproxy_service { 'contrail-config-stats':
    order                  => '205',
    listen_port            => 5937,
    public                 => false,
    internal               => true,
    haproxy_config_options => { 'mode'  => 'http',
                                'stats' => ['enable', 'uri /', 'auth haproxy:contrail123'] },
  }

  openstack::ha::haproxy_service { 'contrail-collector-stats':
    order                  => '206',
    listen_port            => 5938,
    public                 => false,
    internal               => true,
    haproxy_config_options => { 'mode'  => 'http',
                                'stats' => ['enable', 'uri /', 'auth haproxy:contrail123'] },
  }

  openstack::ha::haproxy_service { 'contrail-rabbit':
    order                  => '207',
    listen_port            => 5673,
    balancermember_port    => 5673,
    server_names           => $contrail::rabbit_ips,
    ipaddresses            => $contrail::rabbit_ips,
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
