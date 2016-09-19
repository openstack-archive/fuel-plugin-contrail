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

class contrail::contrail_vmware {

    $phys_dev_facter = regsubst($::contrail::phys_dev, '\.' , '_')
    $dev_mac         = getvar("::macaddress_${phys_dev_facter}")
    $phys_dev        = $contrail::phys_dev

    $install_packages = ['contrail-utils', 'contrail-vrouter-dkms',
      'contrail-vrouter-common', 'contrail-nova-vif', 'iproute2']

    l23network::l3::ifconfig { $contrail::vmware_iface_name: ipaddr => 'none' }

    if !is_pkg_installed('contrail-openstack-vrouter') {
      file { 'create_supervisor_vrouter_override':
        ensure  => present,
        path    => '/etc/init/supervisor-vrouter.override',
        content => 'manual',
        require => Package[$install_packages],
      }
    }

    package { $install_packages:
      ensure => present,
      tag    => ['install'],
    } ->
    file {'/etc/contrail/agent_param':
      ensure  => present,
      content => template('contrail/agent_param.erb'),
      require => Package[$install_packages],
    } ->
    contrail_vrouter_agent_config {
      'DEFAULT/platform'                          : value => 'default';
      'DEFAULT/physical_interface_address'        : value => $contrail::phys_dev_pci;
      'DEFAULT/physical_interface_mac'            : value => $dev_mac;
      'DEFAULT/log_file'                          : value => '/var/log/contrail/contrail-vrouter-agent.log';
      'DEFAULT/log_level'                         : value => 'SYS_NOTICE';
      'DEFAULT/log_local'                         : value => '1';
      'DEFAULT/log_flow'                          : value => '1';
      'DEFAULT/use_syslog'                        : value => '1';
      'DEFAULT/syslog_facility'                   : value => 'LOG_LOCAL0';
      'DEFAULT/headless_mode'                     : value => true;
      'DISCOVERY/server'                          : value => $contrail::contrail_private_vip;
      'DISCOVERY/max_control_nodes'               : value => '2';
      'HYPERVISOR/type'                           : value => 'vmware';
      'HYPERVISOR/vmware_mode'                    : value => 'vcenter';
      'HYPERVISOR/vmware_physical_interface'      : value => $contrail::vmware_iface_name;
      'METADATA/metadata_proxy_secret'            : value => $contrail::metadata_secret;
      'NETWORKS/control_network_ip'               : value => $contrail::address;
      'VIRTUAL-HOST-INTERFACE/name'               : value => 'vhost0';
      'VIRTUAL-HOST-INTERFACE/ip'                 : value => "${contrail::address}/${contrail::netmask_short}";
      'VIRTUAL-HOST-INTERFACE/physical_interface' : value => $contrail::phys_dev;
      'VIRTUAL-HOST-INTERFACE/gateway'            : value => pick($contrail::gateway, false);
      'SERVICE-INSTANCE/netns_command'            : value => '/usr/bin/opencontrail-vrouter-netns';
      'FLOWS/thread_count'                        : value => '2';
    } ->
    contrail_vrouter_nodemgr_config {
      'DISCOVERY/server': value => $contrail::contrail_private_vip;
      'DISCOVERY/port':   value => '5998';
    } ->
    file {'/etc/network/interfaces.d/ifcfg-vhost0':
      ensure  => present,
      content => template('contrail/ubuntu-ifcfg-vhost0.erb'),
    } ->
    exec { 'remove_supervisor_override':
      command => '/bin/rm /etc/init/supervisor-vrouter.override',
      onlyif  => '/usr/bin/test -f /etc/init/supervisor-vrouter.override',
      require => Package[$install_packages],
    } ->
    exec { 'restart_supervisor_vrouter':
      path        => '/usr/bin:/usr/sbin:/bin:/sbin',
      command     => 'service supervisor-vrouter stop && \
    modprobe -r vrouter && \
    sync && \
    echo 3 > /proc/sys/vm/drop_caches && \
    echo 1 > /proc/sys/vm/compact_memory && \
    service supervisor-vrouter start;sleep 10;ip link show vhost0 || exit 1',
      tries       => 3,
      refreshonly => true,
      subscribe   => [Package[$install_packages],
                    File['/etc/contrail/agent_param']
                    ],
    }

    Package[$install_packages] -> Contrail_vrouter_nodemgr_config <||> ~> Exec['restart_supervisor_vrouter']
    Package[$install_packages] -> Contrail_vrouter_agent_config   <||> ~> Exec['restart_supervisor_vrouter']

}
