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
    logoutput => true,
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


define ifup {
  exec { "ifup_${name}":
    command      => "sleep 20; ifup ${name}",
  }
}
  # Configure persistent network device for DPDK VF
  if $contrail::compute_dpdk_on_vf {

    $phys_dev = $contrail::phys_dev

    $vlan_tag            = regsubst($phys_dev, '^.+\.' , '')
    $raw_phys_dev        = regsubst($phys_dev, '\..*' , '')

    # for file_line resources in configure_vfs we need file to be precreated
    file {'/etc/udev/rules.d/72-contrail-dpdk-on-vf.rules':
      ensure  => present,
    }

    $sriov_hash = get_sriov_devices($contrail::phys_dev)

    # this funcition will return undef if overrides are in place
    # otherwise returns bond raw name
    $bond = get_bond_name($contrail::network_scheme, $contrail::phys_dev, $contrail::compute_dpdk_on_vf)
    if $bond {
      include l23network
      exec {"destroy_old_${raw_phys_dev}":
        command => "ifdown ${raw_phys_dev}",
        unless  => "grep dpdk_vf /etc/network/interfaces.d/ifcfg-${raw_phys_dev}",
      }

      $sriov_defaults = {
        'bond_dev_name' => $bond,
      }

      create_resources(contrail::configure_vfs, $sriov_hash, $sriov_defaults)

      $bond_vfs = keys(prefix($sriov_hash, $contrail::vf_prefix))
      $slaves   = join($bond_vfs, ' ')

      l23network::l2::bond { 'bond0':
        interfaces      => [$bond_vfs],
        mtu             => 1500,
        onboot          => true,
        bond_properties => {  # bond configuration properties (see bonding.txt)
          mode             => 'balance-rr',
        },
        delay_while_up => 15,
        provider => lnx,
      }

      file {'/etc/modprobe.d/ixgbe.conf':
        ensure  => file,
        content => 'options ixgbe max_vfs=10',
      } ->

      exec { 'update-initramfs':
        command => 'update-initramfs -u',
      }

      Exec['flush_addr_br_mesh'] -> Exec["destroy_old_${raw_phys_dev}"] ->
      Configure_vfs <||> -> L23Network::L2::Bond <||> ->
      ifup{ $bond_vfs: }

    } else {
        create_resources(contrail::configure_vfs, $sriov_hash)
    }

    # Add vlan interface config if needed
    # In case of bond, this is skipped,
    # vlan interface config provided by l23network
    if ($vlan_tag =~ /^\d*$/ and count(keys($sriov_hash)) == 1 ) {

      $sriov_ifaces  = keys($sriov_hash)
      $pf_dev_name   = $sriov_ifaces[0]
      $dpdk_dev_name = "${contrail::vf_prefix}${pf_dev_name}"

      $vlan_interface_config = join([ "auto ${dpdk_dev_name}.${vlan_tag}",
                                      "iface ${dpdk_dev_name}.${vlan_tag} inet manual",
                                      "vlan-raw-device ${dpdk_dev_name}",
                                    ],"\n")

      file {"/etc/network/interfaces.d/ifcfg-${dpdk_dev_name}.${vlan_tag}":
        ensure  => file,
        content => $vlan_interface_config,
      }
      Configure_vfs <||> ->
      exec { "ifup_${dpdk_dev_name}.${vlan_tag}":
        command => "ifup ${dpdk_dev_name}.${vlan_tag}",
        unless  => "ip link show dev ${dpdk_dev_name}.${vlan_tag} | grep ,UP",
        require => [File["/etc/network/interfaces.d/ifcfg-${dpdk_dev_name}.${vlan_tag}"],
                    File["/etc/network/interfaces.d/ifcfg-${dpdk_dev_name}"],
                    ]
      }
    }
  }

}
