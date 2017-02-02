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

class contrail::provision::api_readiness {
  define check {
    exec {$title:
      command   => "bash -c 'if ! [[ $(curl -s -o /dev/null -w \"%{http_code}\" http://${contrail::contrail_mgmt_vip}:${contrail::api_server_port}) =~ ^(200|401)$ ]]; then exit 1; fi'",
      tries     => 10,
      try_sleep => 10,
      unless    => "test -e ${title}",
    }
    contain ::osnailyfacter::wait_for_keystone_backends
  }
}
