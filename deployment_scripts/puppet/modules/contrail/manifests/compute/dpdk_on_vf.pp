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

class contrail::compute::dpdk_on_vf {

  if $contrail::compute_dpkd_on_vf {
    $vf_data = get_fv_data($contrail::phys_dev, $contrail::dpdk_vf_number)
    $dpdk_dev_name = "dpdk-vf${contrail::dpdk_vf_number}"
    $dpdk_vf_origin_name = $vf_data['vf_dev_name']
    $dpdk_dev_pci = $vf_data['vf_pci_addr']
    $dpdk_dev_mac = $vf_data['vf_mac_addr']
    $phys_dev = $dpdk_dev_name
    $pci_wl = generate_passthrough_whitelist(
      $contrail::sriov_physnet,
      $contrail::compute_dpkd_on_vf,
      $contrail::phys_dev,
      $contrail::dpdk_vf_number
      )

    exec { 'rename-dpdk-vf':
      path    => '/bin:/usr/bin:/usr/sbin',
      command => "ip link set ${dpdk_vf_origin_name} name ${dpdk_dev_name}",
      unless  => 'ip link | grep vhost0',
    }

    file {'/etc/udev/rules.d/72-contrail-dpdk-on-vf.rules':
      ensure  => present,
      content => template('contrail/72-contrail-dpdk-on-vf.rules.erb'),
    }

    contrail_vrouter_agent_config {
      'DEFAULT/log_file':                          value => '/var/log/contrail/contrail-vrouter-agent.log';
      'DEFAULT/log_level':                         value => 'SYS_NOTICE';
      'DEFAULT/log_local':                         value => '1';
      'DEFAULT/log_flow':                          value => '1';
      'DEFAULT/use_syslog':                        value => '1';
      'DEFAULT/syslog_facility':                   value => 'LOG_LOCAL0';
      'DEFUALT/headless_mode':                     value => true;
      'DISCOVERY/server':                          value => $contrail::contrail_private_vip;
      'DISCOVERY/max_control_nodes':               value => '2';
      'HYPERVISOR/type':                           value => 'kvm';
      'METADATA/metadata_proxy_secret':            value => $contrail::metadata_secret;
      'NETWORKS/control_network_ip':               value => $contrail::address;
      'VIRTUAL-HOST-INTERFACE/name':               value => 'vhost0';
      'VIRTUAL-HOST-INTERFACE/ip':                 value => "${contrail::address}/${contrail::netmask_short}";
      'VIRTUAL-HOST-INTERFACE/physical_interface': value => $contrail::phys_dev;
      'VIRTUAL-HOST-INTERFACE/gateway':            value => pick($contrail::gateway, false);
      'SERVICE-INSTANCE/netns_command':            value => '/usr/bin/opencontrail-vrouter-netns';
    }

    nova_config {
      'DEFAULT/pci_passthrough_whitelist':       value => $pci_wl;
    } ~>

    service { 'nova-compute':
      ensure => running,
      enable => true,
    }

    service {'supervisor-vrouter':
      ensure    => running,
      enable    => true,
      subscribe => [Exec['rename-dpdk-vf']],
    }

    Contrail_vrouter_agent_config <||> ~> Service['supervisor-vrouter']

  }
}
