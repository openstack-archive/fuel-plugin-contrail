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


define contrail::rclocal_vfs (
  $totalvfs,
  $numvfs,
  $physnet        = $::contrail::sriov_physnet,
  $network_device = $title,
  )
{

  if (versioncmp($::libnl_version, '3.2.21-1') > 0) {
    $final_vf = $totalvfs
  } else {
    $final_vf = min(30, $totalvfs)
  }

  file {"/etc/network/interfaces.d/ifcfg-${network_device}":
    content => "auto ${network_device}\niface ${network_device} inet manual\n"
  }

  file_line {"sriov ${network_device}":
    line  => "echo ${final_vf} > /sys/class/net/${network_device}/device/sriov_numvfs",
    path  => '/etc/rc.local',
    match => ".* /sys/class/net/${network_device}/device/sriov_numvfs"
  }

}
