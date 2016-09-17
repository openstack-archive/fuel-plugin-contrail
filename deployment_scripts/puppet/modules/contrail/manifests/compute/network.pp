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
    path => '/usr/bin:/bin:/sbin:/usr/sbin',
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

  # Configure persistent network device for DPDK VF
  if $contrail::compute_dpdk_on_vf {

    $vf_data = get_vf_data($contrail::phys_dev, $contrail::dpdk_vf_number)
    $dpdk_dev_name = "dpdk-vf${contrail::dpdk_vf_number}"
    $dpdk_vf_origin_name = $vf_data['vf_dev_name']
    $dpdk_dev_pci = $vf_data['vf_pci_addr']
    $dpdk_dev_mac = $vf_data['vf_mac_addr']
    $raw_phys_dev = regsubst($::contrail::phys_dev, '\..*' , '')
    exec { 'rename-dpdk-vf':
      command => "ip link set ${dpdk_vf_origin_name} name ${dpdk_dev_name}",
      unless  => "ip link | grep ${dpdk_dev_name}",
    }

    file {'/etc/udev/rules.d/72-contrail-dpdk-on-vf.rules':
      ensure  => present,
      content => template('contrail/72-contrail-dpdk-on-vf.rules.erb'),
    }

    $interface_config = join(["auto ${dpdk_dev_name}",
                            "iface ${dpdk_dev_name} inet manual",
                            "pre-up ip link set link dev ${raw_phys_dev} vf ${contrail::dpdk_vf_number} vlan 0",
                            "post-up ip link set link dev ${raw_phys_dev} vf ${contrail::dpdk_vf_number} spoof off",
                            ],"\n")
    # Add vlan interface config if needed
    if ($::contrail::phys_dev != $raw_phys_dev) {

      $vlan_tag = regsubst($::contrail::phys_dev, '^.+\.' , '')
      $vlan_interface_config = join(["auto ${dpdk_dev_name}.${vlan_tag}",
                                     "iface ${dpdk_dev_name}.${vlan_tag} inet manual",
                                     "vlan-raw-device dpdk_dev_name"
                                    ],"\n")

      file {"/etc/network/interfaces.d/ifcfg-${dpdk_dev_name}.${vlan_tag}":
        ensure  => file,
        content => $vlan_interface_config,
        require => [File['/etc/udev/rules.d/72-contrail-dpdk-on-vf.rules'],
                    File["/etc/network/interfaces.d/ifcfg-${dpdk_dev_name}"],
                    ],
      }

      exec { "ifup_${dpdk_dev_name}.${vlan_tag}":
        command      => "ifup ${dpdk_dev_name}.${vlan_tag}",
        unless       => "ip link show dev ${dpdk_dev_name}.${vlan_tag} | grep ,UP",
        require      => [File["/etc/network/interfaces.d/ifcfg-${dpdk_dev_name}.${vlan_tag}"],
                         Exec["ifup_${dpdk_dev_name}"],
                         ],
      }

    }

    file {"/etc/network/interfaces.d/ifcfg-${dpdk_dev_name}":
      ensure  => file,
      content => $interface_config,
      require => File['/etc/udev/rules.d/72-contrail-dpdk-on-vf.rules'],
    }

    exec { "ifup_${dpdk_dev_name}":
      command      => "ifup ${dpdk_dev_name}",
      unless       => "ip link show dev ${dpdk_dev_name} | grep ,UP",
      require      => File["/etc/network/interfaces.d/ifcfg-${dpdk_dev_name}"],
    }
  }

}
