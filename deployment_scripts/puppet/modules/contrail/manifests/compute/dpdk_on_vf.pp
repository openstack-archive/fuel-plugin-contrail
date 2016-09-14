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

  if $contrail::compute_dpdk_on_vf {
    $vf_data = get_vf_data($contrail::phys_dev, $contrail::dpdk_vf_number)
    $dpdk_dev_name = "dpdk-vf${contrail::dpdk_vf_number}"
    $dpdk_vf_origin_name = $vf_data['vf_dev_name']
    $dpdk_dev_pci = $vf_data['vf_pci_addr']
    $dpdk_dev_mac = $vf_data['vf_mac_addr']
    $phys_dev = $dpdk_dev_name
    $pci_wl = generate_passthrough_whitelist(
      $contrail::dpdk_physnet,
      $contrail::compute_dpdk_on_vf,
      $contrail::phys_dev,
      $contrail::dpdk_vf_number
      )

    $sriov_hash = get_sriov_devices($contrail::compute_dpdk_on_vf, $contrail::phys_dev)
    create_resources(contrail::create_vfs, $sriov_hash)

    exec { 'rename-dpdk-vf':
      path    => '/bin:/usr/bin:/usr/sbin',
      command => "ip link set ${dpdk_vf_origin_name} name ${dpdk_dev_name}",
      unless  => "ip link | grep ${dpdk_dev_name}",
    }

    $interface_config = join(["auto ${dpdk_dev_name}",
                            "iface ${dpdk_dev_name} inet manual",
                            ],"\n")

    file {"/etc/network/interfaces.d/ifcfg-${dpdk_dev_name}":
      ensure  => file,
      content => $interface_config,
    }

    file {'/etc/udev/rules.d/72-contrail-dpdk-on-vf.rules':
      ensure  => present,
      content => template('contrail/72-contrail-dpdk-on-vf.rules.erb'),
    }

    nova_config {
      'DEFAULT/pci_passthrough_whitelist':       value => $pci_wl;
    } ~>

    service { 'nova-compute':
      ensure => running,
      enable => true,
    }
  }
}
