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

Exec { path => '/bin:/sbin:/usr/bin:/usr/sbin', refresh => 'echo NOOP_ON_REFRESH'}

# Temporary dirty hack. Network configuration fails because of deployed contrail [FIXME]
############################################################################
exec {'no_predefined_network_hack':
  command => 'sed -i -e "82s/.*/\tif\ false\ {/" /etc/puppet/modules/osnailyfacter/modular/openstack-network/openstack-network-controller.pp'
}

exec {'no_network_reconfigure':
  command => 'echo "#NOOP here. Modified by contrail plugin" > /etc/puppet/modules/osnailyfacter/modular/netconfig/netconfig.pp',
  onlyif => 'test -f /opt/contrail/provision-vrouter-DONE'
}

exec {'no_openstack_network_reconfigure':
  command => 'echo "#NOOP here. Modified by contrail plugin" > /etc/puppet/modules/osnailyfacter/modular/openstack-network/openstack-network-compute.pp',
  onlyif => 'test -f /opt/contrail/provision-vrouter-DONE'
}
############################################################################

case $operatingsystem
{
    CentOS:
      {
        yumrepo {'mos': priority => 1, exclude => 'python-thrift,nodejs'} # Contrail requires newer python-thrift and nodejs from it's repo
        package {'yum-plugin-priorities': ensure => present }
      }
    default: {}
}
