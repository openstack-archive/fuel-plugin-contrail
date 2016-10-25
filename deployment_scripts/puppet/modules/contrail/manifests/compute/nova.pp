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

  $cgroup_acl_string='["/dev/null", "/dev/full", "/dev/zero","/dev/random", "/dev/urandom","/dev/ptmx","/dev/kvm", "/dev/kqemu","/dev/rtc","/dev/hpet", "/dev/vfio/vfio","/dev/net/tun"]'

  ini_setting { 'set_cgroup_acl_string':
    ensure  => present,
    path    => '/etc/libvirt/qemu.conf',
    setting => 'cgroup_device_acl',
    value   => $cgroup_acl_string,
  } ~>
  service { $contrail::libvirt_name :
    ensure => 'running',
    enable => true
  }

  nova_config {
    'DEFAULT/network_api_class':                 value => 'nova.network.neutronv2.api.API';
    'DEFAULT/neutron_url_timeout':               value => '300';
    'DEFAULT/firewall_driver':                   value => 'nova.virt.firewall.NoopFirewallDriver';
    'DEFAULT/security_group_api':                value => 'neutron';
    'DEFAULT/heal_instance_info_cache_interval': value => '0';
  }

  if $contrail::compute_dpdk_enabled {
    if $contrail::compute_dpdk_on_vf {
      $pci_wl = generate_passthrough_whitelist(
        $contrail::dpdk_physnet,
        $contrail::compute_dpdk_on_vf,
        $contrail::phys_dev,
        $contrail::dpdk_vf_number
      )
      nova_config {
        'DEFAULT/pci_passthrough_whitelist':       value => $pci_wl;
      }
    }
    nova_config {
      'libvirt/virt_type': value => 'kvm';
      'CONTRAIL/use_userspace_vhost': value => true;
    }

    file { '/etc/nova/nova-compute.conf':
      ensure  => present,
      content => '',
    }

    $ceph_manifest = '/etc/puppet/modules/ceph/manifests/nova_compute.pp'
    file_line { 'Replace libvirt service name':
      path  => $ceph_manifest,
      line  => '    name   => "libvirt-bin",',
      match => 'nova::params::libvirt_service_name',
    }

  }

  Nova_config <||> ~>
  service { 'nova-compute':
    ensure => running,
    enable => true,
  }

}
