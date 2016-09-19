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


define contrail::create_vfs (
  $totalvfs,
  $numvfs,
  $network_device = $title,
  )
{

  Exec {
    provider => 'shell',
    path => '/usr/bin:/bin:/sbin',
  }

  $bond = get_bond_name($contrail::network_scheme, $contrail::phys_dev, $contrail::compute_dpdk_on_vf)


  $interface_config_array = [ "auto ${network_device}",
                              "iface ${network_device} inet manual",
                              "post-up echo ${totalvfs} > /sys/class/net/${network_device}/device/sriov_numvfs",
                              "post-up ip link set link dev ${network_device} vf ${contrail::dpdk_vf_number} spoof off", '',
                              ]

  if !$bond {
    $interface_config=join(concat($interface_config_array, "post-up ip link set link dev ${network_device} vf ${contrail::dpdk_vf_number} vlan 0"), "\n")
    } else {
      $interface_config=join($interface_config_array, "\n")
    }

  file {"/etc/network/interfaces.d/ifcfg-${network_device}":
    ensure  => file,
    content => $interface_config,
  }

  exec {"create_vfs_on_${network_device}":
    command => "echo ${totalvfs} > /sys/class/net/${network_device}/device/sriov_numvfs",
  }

}
