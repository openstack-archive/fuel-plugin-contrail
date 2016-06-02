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

class contrail::compute::firewall {

  firewallchain {
    [
      'INPUT:nat:IPv4',
      'OUTPUT:nat:IPv4',
      'POSTROUTING:nat:IPv4',
      'PREROUTING:nat:IPv4'
    ]:
      purge => true,
  }

  firewall { '0000 metadata service':
    source  => '169.254.0.0/16',
    iniface => 'vhost0',
    action  => 'accept'
  }

  firewall { '0001 juniper contrail rules':
    proto  => 'tcp',
    dport  => ['2049','8085','9090','8102','33617','39704','44177','55970','60663'],
    action => 'accept'
  }
}
