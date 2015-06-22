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

# Network configuration fails because of deployed contrail
exec {'no_predefined_network_hack':
  command => 'sed -i -e "82s/.*/\tif\ false\ {/" /etc/puppet/modules/osnailyfacter/modular/openstack-network/openstack-network-controller.pp'
}

case $operatingsystem
{
    CentOS:
      {
        yumrepo {'mos': priority => 1, exclude => 'python-thrift,nodejs'} # Contrail requires newer python-thrift and nodejs from it's repo
        yumrepo {'contrail-1.0.0': exclude => 'python-pycrypto'} # Conflicts with python-crypto@mos. Provides same files.
        package {'yum-plugin-priorities': ensure => present }
      }
}
