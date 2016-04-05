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

$settings = hiera('contrail', {})
$global_dpdk_enabled  = $settings['contrail_global_dpdk']
$compute_dpdk_enabled = $global_dpdk_enabled and 'dpdk' in hiera_array('roles')

File {
  ensure  => present,
  mode    => '0644',
  owner   => root,
  group   => root,
}

Exec {
  provider => 'shell',
  path     => '/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin',
}

apt::pin { 'contrail-main':
  explanation => 'Set priority for common contrail packages',
  priority    => 200,
  label       => 'contrail',
}

# Temporary dirty hack. Network configuration fails because of deployed contrail vrouter [FIXME]
$osnailyfacter_path = '/etc/puppet/modules/osnailyfacter'

exec {'no_network_reconfigure':
  command => "/bin/echo '#NOOP here. Modified by contrail plugin' > ${osnailyfacter_path}/modular/netconfig/netconfig.pp",
  onlyif => '/usr/bin/test -f /opt/contrail/provision-vrouter-DONE'
}

exec {'no_openstack_network_reconfigure':
  command => "/bin/echo '#NOOP here. Modified by contrail plugin' > ${osnailyfacter_path}/modular/openstack-network/openstack-network-compute.pp",
  onlyif => '/usr/bin/test -f /opt/contrail/provision-vrouter-DONE'
}

# Temporary fix for ceph manifests from fuel-library
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

if $compute_dpdk_enabled {
  # Create local dpdk repository
  package { 'dpdk-depends-packages':
    ensure => present,
  } ->
  exec { 'update-dpdk-repo':
    command => 'dpkg-scanpackages . /dev/null | gzip -9c > Packages.gz',
    cwd     => '/opt/contrail/contrail_install_repo_dpdk',
  } ->
  file {'/opt/contrail/contrail_install_repo_dpdk/Release':
    ensure  => file,
    content => 'Label: dpdk-depends-packages',
  } ->
  apt::source { 'dpdk-depends-repo':
    location    => 'file:/opt/contrail/contrail_install_repo_dpdk',
    repos       => './',
    release     => '',
    include_src => false,
  }
}
