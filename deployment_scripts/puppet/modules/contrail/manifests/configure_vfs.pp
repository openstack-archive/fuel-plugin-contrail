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
define contrail::configure_vfs (
  $numvfs,
  $totalvfs,
  $pf_dev_name = $title,
  $bond_dev_name = undef,
  ) {

  Exec {
    provider => 'shell',
    path => '/usr/bin:/bin:/sbin:/usr/sbin',
  }

  $vf_data           = get_vf_data($pf_dev_name, $contrail::dpdk_vf_number)
  $vf_dev_name       = "${contrail::vf_prefix}${pf_dev_name}"
  $vf_number         = $contrail::dpdk_vf_number
  $vf_origin_name    = $vf_data['vf_dev_name']
  $vf_dev_pci        = $vf_data['vf_pci_addr']
  $vf_dev_mac        = $vf_data['vf_mac_addr']

  $udev_rule = join(['SUBSYSTEM=="net"',
                    'ACTION=="add"',
                    "KERNELS==\"${vf_dev_pci}\"",
                    "NAME=\"${vf_dev_name}\"",
                    "RUN+=\"/bin/ip link set dev %k address ${vf_dev_mac}\"",
                    ],', ')

  $interface_config_array = ["auto ${vf_dev_name}",
                            "iface ${vf_dev_name} inet manual",
                            "hwaddress ether ${vf_dev_mac}",
                            "pre-up ip link set link dev ${pf_dev_name} vf ${vf_number} spoof off"
                            ]

  $dpdk_vrouter_up = 'pgrep -f "^/usr/bin/contrail-vrouter-dpdk"'
#  $dpdk_vrouter_up = 'false'

  if !$bond_dev_name {
    $interface_config=join(concat($interface_config_array, "pre-up ip link set link dev ${pf_dev_name} vf ${vf_number} vlan 0"), "\n")

    file {"/etc/network/interfaces.d/ifcfg-${vf_dev_name}":
      ensure  => file,
      content => $interface_config,
    }
  }

  file_line {"udev_rule_for_${vf_dev_name}":
    line    => $udev_rule,
    path    => '/etc/udev/rules.d/72-contrail-dpdk-on-vf.rules',
    require => File['/etc/udev/rules.d/72-contrail-dpdk-on-vf.rules'],
  } ->

  exec { "ifup_${pf_dev_name}":
    command => "ifup ${pf_dev_name}",
    unless  => ["ip link show ${pf_dev_name} | grep ,UP",
                $dpdk_vrouter_up]
  } ->

  exec { "rename-${vf_dev_name}":
    command => "ip link set ${vf_origin_name} name ${vf_dev_name}",
    unless  => ["ip link | grep ${vf_dev_name}",
                $dpdk_vrouter_up]
  }


  if !$bond_dev_name {
    exec { "ifup_${vf_dev_name}":
      command => "ifup ${vf_dev_name}",
      unless  => ["ip link show ${vf_dev_name} | grep ,UP",
                  $dpdk_vrouter_up],
      require => [File["/etc/network/interfaces.d/ifcfg-${vf_dev_name}"],
                  Exec["rename-${vf_dev_name}"]]
    }
  }



}
