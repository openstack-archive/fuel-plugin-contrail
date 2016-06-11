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

class contrail::compute::vrouter {

# facter uses underscore instead of dot as a separator for interface name with vlan
$phys_dev_facter = regsubst($::contrail::phys_dev, '\.' , '_')
$dev_mac         = getvar("::macaddress_${phys_dev_facter}")

  if $contrail::compute_dpdk_enabled {
    if empty($dev_mac) {
      $dpdk_dev_mac = get_mac_from_vrouter()
    } else {
      $dpdk_dev_mac = $dev_mac
    }

    $raw_phys_dev = regsubst($::contrail::phys_dev, '\..*' , '')
    # in case of bonds, MAC address should be set permanently, because slave interfaces
    # may start in random order during the boot process
    if ( 'bond' in $raw_phys_dev) {
      file_line { 'permanent_mac':
        ensure => present,
        line => "hwaddress ${dev_mac}",
        path => "/etc/network/interfaces.d/ifcfg-${raw_phys_dev}",
        after => "iface ${raw_phys_dev} inet manual",
      }
    }

    $install_packages = ['contrail-openstack-vrouter','contrail-vrouter-dpdk-init','iproute2','haproxy','libatm1']
    $delete_packages  = ['openvswitch-common','openvswitch-datapath-dkms','openvswitch-datapath-lts-saucy-dkms','openvswitch-switch','nova-network','nova-api']
    file {'/etc/contrail/supervisord_vrouter_files/contrail-vrouter-dpdk.ini':
      ensure  => present,
      content => template('contrail/contrail-vrouter-dpdk.ini.erb'),
      require => Class[Contrail::Package],
      notify  => Service['supervisor-vrouter'],
    }
  } else {
    $install_packages = ['contrail-openstack-vrouter','contrail-vrouter-dkms','iproute2','haproxy','libatm1']
    $delete_packages  = ['openvswitch-common','openvswitch-datapath-dkms','openvswitch-datapath-lts-saucy-dkms','openvswitch-switch','nova-network','nova-api']
  }

  if !is_pkg_installed('contrail-openstack-vrouter') {
    file { 'create_supervisor_vrouter_override':
      ensure  => present,
      path    => '/etc/init/supervisor-vrouter.override',
      content => 'manual',
      before  => Class['contrail::package'],
    }
  }

  class { 'contrail::package':
    install => [$install_packages],
    remove  => [$delete_packages],
  } ->
  exec { 'remove-ovs-modules':
    command => '/sbin/modprobe -r openvswitch',
    onlyif  => '/sbin/lsmod | grep -q openvswitch',
  } ->
  file {'/etc/contrail/agent_param':
    ensure  => present,
    content => template('contrail/agent_param.erb'),
    require => Class[Contrail::Package],
  } ->
  file {'/etc/contrail/contrail-vrouter-agent.conf':
    ensure  => present,
    content => template('contrail/contrail-vrouter-agent.conf.erb'),
  } ->
  file {'/etc/contrail/contrail-vrouter-nodemgr.conf':
    ensure  => present,
    content => template('contrail/contrail-vrouter-nodemgr.conf.erb'),
  }
  exec { 'remove_supervisor_override':
    command => '/bin/rm /etc/init/supervisor-vrouter.override',
    onlyif  => '/usr/bin/test -f /etc/init/supervisor-vrouter.override',
    require => Class['Contrail::Package'],
  } ->
  service {'supervisor-vrouter':
    ensure    => running,
    enable    => true,
    subscribe => [Class[Contrail::Package],Exec['remove-ovs-modules'],
                  File['/etc/contrail/agent_param','/etc/contrail/contrail-vrouter-agent.conf',
                  '/etc/contrail/contrail-vrouter-nodemgr.conf']
                  ],
  }
  # Override network_scheme to skip interfaces used by the vrouter
  $override_ns = vrouter_override_network_scheme($contrail::network_scheme, $contrail::phys_dev, $contrail::compute_dpdk_enabled)
  file { '/etc/hiera/plugins/contrail-vrouter-override_ns.yaml':
    ensure  => file,
    content => inline_template('<%= YAML.dump @override_ns %>'),
    require => Service['supervisor-vrouter'],
    replace => false,
  } ->
  file_line {'contrail-vrouter-override_ns':
    path  => '/etc/hiera.yaml',
    line  => '    - plugins/contrail-vrouter-override_ns',
    after => '  !ruby/sym hierarchy:',
  }
}
