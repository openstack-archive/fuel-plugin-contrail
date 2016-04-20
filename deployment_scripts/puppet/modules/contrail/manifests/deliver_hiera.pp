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


define contrail::deliver_hiera (
  $host = $title,
  )
{
  exec {"create_override_dir_${host}":
    path    => ['/bin', '/usr/bin'],
    command => "ssh root@${host} 'mkdir -p /etc/hiera/override/'",
  } ->

  exec {"copy_yaml_to_config_node_${host}":
    path    => ['/bin', '/usr/bin'],
    command => "scp -oStrictHostKeyChecking=no -i /var/lib/astute/vmware/vmware /root/config-override.yaml root@${host}:/etc/hiera/override/plugins.yaml",
  }

}
