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

notice('MODULAR: contrail/contrail-compute-repo.pp')

File {
  ensure  => present,
  mode    => '0644',
  owner   => root,
  group   => root,
}

apt::pin { 'contrail-main':
  explanation => 'Set priority for common contrail packages',
  priority    => 200,
  label       => 'contrail',
}

# Temporary dirty hack. Network configuration fails because of deployed contrail vrouter [FIXME]
$osnailyfacter_path = '/etc/puppet/modules/osnailyfacter'

file { "${osnailyfacter_path}/modular/netconfig/netconfig.pp":
  ensure  => file,
  content => '#NOOP here. Modified by contrail plugin',
  onlyif  => '/usr/bin/test -f /opt/contrail/provision-vrouter-DONE',
}

file { "${osnailyfacter_path}/modular/openstack-network/openstack-network-compute.pp":
  ensure  => file,
  content => '#NOOP here. Modified by contrail plugin',
  onlyif  => '/usr/bin/test -f /opt/contrail/provision-vrouter-DONE',
}

file { "${osnailyfacter_path}/lib/puppet/parser/functions/roles_include.rb":
  source  => 'puppet:///modules/contrail/roles_include.rb',
}

file { "${osnailyfacter_path}/lib/puppet/parser/functions/get_node_key_name.rb":
  source  => 'puppet:///modules/contrail/get_node_key_name.rb',
}

file_line { 'roles':
  path  => '/etc/puppet/modules/ceph/manifests/init.pp',
  line  => " if roles_include(['primary-controller', 'controller', 'ceph-mon', 'ceph-osd', 'compute', 'cinder']) {",
  match => 'controller\|ceph\|compute\|cinder',
}