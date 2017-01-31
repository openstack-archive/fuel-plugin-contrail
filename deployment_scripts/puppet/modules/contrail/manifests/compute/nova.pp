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

class contrail::compute::nova {

  $cgroup_acl_string='["/dev/null", "/dev/full", "/dev/zero", "/dev/random", "/dev/urandom", "/dev/ptmx", "/dev/kvm", "/dev/kqemu", "/dev/rtc", "/dev/hpet", "/dev/vfio/vfio", "/dev/net/tun"]'

  ini_setting { 'set_cgroup_acl_string':
    ensure  => present,
    path    => '/etc/libvirt/qemu.conf',
    setting => 'cgroup_device_acl',
    value   => $cgroup_acl_string,
    notify  => Service['libvirt'],
  }

  # [LCM] Workaroud to fix duplicate declaration with Service['libvirt']
  # from class 'nova::compute::libvirt' during catalog compilation.
  if !defined(Service['libvirt']) {
    service { 'libvirt':
      ensure => 'running',
      enable => true,
      name   => $contrail::libvirt_name,
    }
  }

  # [LCM] Workaroud to fix duplicate declaration with nova_config recources
  # from class 'nova::network::neutron' during catalog compilation.
  if !defined(Nova_config['DEFAULT/network_api_class']) {
    nova_config {'DEFAULT/network_api_class':
      value => 'nova.network.neutronv2.api.API'
    }
  }
  else {
    Nova_config <| (title == 'DEFAULT/network_api_class') |> {
      value => 'nova.network.neutronv2.api.API',
    }
  }

  if !defined(Nova_config['DEFAULT/firewall_driver']) {
    nova_config {'DEFAULT/firewall_driver':
      value => 'nova.virt.firewall.NoopFirewallDriver'
    }
  }
  else {
    Nova_config <| (title == 'DEFAULT/firewall_driver') |> {
      value => 'nova.virt.firewall.NoopFirewallDriver',
    }
  }

  if !defined(Nova_config['DEFAULT/security_group_api']) {
    nova_config {'DEFAULT/security_group_api':
      value => 'neutron'
    }
  }
  else {
    Nova_config <| (title == 'DEFAULT/security_group_api') |> {
      value => 'neutron',
    }
  }

  if !defined(Nova_config['neutron/timeout']) {
    nova_config {'neutron/timeout' : value => '300' }
  }

  # [LCM] Workaroud to fix duplicate declaration with nova_config recource
  # from class 'nova::compute' during catalog compilation.
  if !defined(Nova_config['DEFAULT/heal_instance_info_cache_interval']) {
    nova_config { 'DEFAULT/heal_instance_info_cache_interval':
      value => '0',
    }
  }
  else {
    Nova_config <| (title == 'DEFAULT/heal_instance_info_cache_interval') |> {
      value => '0',
    }
  }

  if $contrail::compute_dpdk_enabled {
    nova_config {
      'CONTRAIL/use_userspace_vhost': value => true;
    }
  }

  # [LCM] Workaroud to fix duplicate declaration with Service['nova-compute']
  # from class 'nova::generic_service' during catalog compilation.
  if !defined(Class['::nova::compute']) {
    service { 'nova-compute':
      ensure => running,
      enable => true,
    }
  }else{
    Service<| title == 'nova-compute' |> {
      ensure     => running,
      enable     => true,
      hasstatus  => true,
      hasrestart => true,
    }
  }

  Nova_config <||> ~> Service['nova-compute']
}
