#    Copyright 2015 Mirantis, Inc.
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
  $network_device = $title,
  $vf_user_specified,
  $phys_name = "temp"
  )
{

  if (versioncmp($::libnl_version, '3.2.21-1') > 0) {
    $final_vf = $vf_user_specified
  } else {
    $final_vf = min($vf_user_specified, 30)
  }

  file_line {"sriov ${title}":
    line  => "echo ${final_vf} > /sys/class/net/${network_device}/device/sriov_numvfs",
    path  => '/etc/rc.local',
    match => ".* /sys/class/net/${network_device}/device/sriov_numvfs"
  }

}