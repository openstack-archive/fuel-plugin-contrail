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

class contrail::contrail::compute_repo {

  apt::pin { 'contrail-main':
    explanation => 'Set priority for common contrail packages',
    priority    => 200,
    label       => 'contrail',
  }

  # Temporary dirty hack. Network configuration fails because of deployed contrail vrouter [FIXME]
  exec {'no_network_reconfigure':
    command => '/bin/echo "#NOOP here. Modified by contrail plugin" > /etc/puppet/modules/osnailyfacter/modular/netconfig/netconfig.pp',
    onlyif  => '/usr/bin/test -f /opt/contrail/provision-vrouter-DONE'
  }
  exec {'no_openstack_network_reconfigure':
    command => '/bin/echo "#NOOP here. Modified by contrail plugin" > /etc/puppet/modules/osnailyfacter/modular/openstack-network/openstack-network-compute.pp',
    onlyif  => '/usr/bin/test -f /opt/contrail/provision-vrouter-DONE'
  }
}
