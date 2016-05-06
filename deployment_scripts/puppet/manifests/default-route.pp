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

notice('MODULAR: contrail/default-route.pp')

# configure_default_route task from fuel-library adds IP back to bridge
# with 'management' role. while this is fine for usual deployments, it
# is not what needed in case of network template where management, storage and
# private are binded to same interface.

$gw = hiera('management_vrouter_vip', {})

exec { 'prov_config_node':
  provider => 'shell',
  path     => '/usr/bin:/bin:/sbin',
  command  => "ip route add default via ${gw} | exit 0",
}
