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

class contrail::compute::network {
  $address        = $contrail::address
  $ifname         = $contrail::phys_dev
  $netmask        = $contrail::netmask_short
  $default_gw     = undef

  Exec {
    provider => 'shell',
    path => '/usr/bin:/bin:/sbin',
  }

  file { '/etc/network/interfaces.d/ifcfg-br-mesh':
    ensure => absent,
  } ->
  # Remove interface from the bridge
  exec {"remove_${ifname}_mesh":
    command => "brctl delif br-mesh ${ifname}",
    returns => [0,1] # Idempotent
  } ->
  exec {'flush_addr_br_mesh':
    command => 'ip addr flush dev br-mesh',
    returns => [0,1] # Idempotent
  }
  file {'/etc/network/interfaces.d/ifcfg-vhost0':
    ensure  => present,
    content => template('contrail/ubuntu-ifcfg-vhost0.erb'),
  }

  # Configure persistent network device for DPDK VF
  if $contrail::compute_dpdk_on_vf {
    $sriov_hash = get_sriov_devices($contrail::compute_dpdk_on_vf, $contrail::phys_dev)
    create_resources(contrail::create_vfs, $sriov_hash)

    $vf_data = get_vf_data($contrail::phys_dev, $contrail::dpdk_vf_number)
    $dpdk_dev_name = "dpdk-vf${contrail::dpdk_vf_number}"
    $dpdk_vf_origin_name = $vf_data['vf_dev_name']
    $dpdk_dev_pci = $vf_data['vf_pci_addr']
    $dpdk_dev_mac = $vf_data['vf_mac_addr']
    $phys_dev = $dpdk_dev_name

    file {'/etc/udev/rules.d/72-contrail-dpdk-on-vf.rules':
      ensure  => present,
      content => template('contrail/72-contrail-dpdk-on-vf.rules.erb'),
    }

    $interface_config = join(["auto ${dpdk_dev_name}",
                            "iface ${dpdk_dev_name} inet manual",
                            ],"\n")

    file {"/etc/network/interfaces.d/ifcfg-${dpdk_dev_name}":
      ensure  => file,
      content => $interface_config,
      require => File['/etc/udev/rules.d/72-contrail-dpdk-on-vf.rules'],
    }

    File['/etc/udev/rules.d/72-contrail-dpdk-on-vf.rules'] -> Exec<| tag == 'create_vfs' |>
  }
}
