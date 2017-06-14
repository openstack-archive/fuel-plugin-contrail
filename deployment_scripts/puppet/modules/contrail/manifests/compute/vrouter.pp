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

  $raw_phys_dev = regsubst($::contrail::phys_dev, '\..*' , '')
  $vlan_tag = regsubst($::contrail::phys_dev, '^.+\.' , '')

  if $contrail::compute_dpdk_on_vf {

    $sriov_hash    = get_sriov_devices($contrail::phys_dev)
    $sriov_ifaces  = keys($sriov_hash)
    $pf_dev_name   = $sriov_ifaces[0]
    $dpdk_dev_name = "${contrail::vf_prefix}${pf_dev_name}"

    # unbonded VFs go here
    if count(keys($sriov_hash)) == 1 {

      if $vlan_tag =~ /^\d*$/ {
        $phys_dev = "${dpdk_dev_name}.${vlan_tag}"
      } else {
        $phys_dev = $dpdk_dev_name
      }

      $vf_data       = get_vf_data($pf_dev_name, $contrail::dpdk_vf_number)
      $dpdk_dev_pci  = $vf_data['vf_pci_addr']
      $dev_mac       = $vf_data['vf_mac_addr']

    # bonds from VFs go here
    } else {

        $phys_dev     = $contrail::phys_dev
        $dev_mac      = getvar("::macaddress_${dpdk_dev_name}")
        $dpdk_dev_pci = $contrail::phys_dev_pci

    }

  # usual dpdk and kernel-based routers go here
  } else {
      # facter uses underscore instead of dot as a separator for interface name with vlan
      $phys_dev_facter = regsubst($::contrail::phys_dev, '\.' , '_')
      $dev_mac         = getvar("::macaddress_${phys_dev_facter}")
      $phys_dev        = $contrail::phys_dev
      $dpdk_dev_pci    = $contrail::phys_dev_pci
  }

  Exec {
    path => '/sbin:/usr/sbin:/bin:/usr/bin',
  }

  if $contrail::compute_dpdk_enabled {

    $mac_from_vrouter = $::mac_from_vrouter
    if $contrail::compute_dpdk_on_vf {
      $dpdk_dev_mac = $dev_mac
    } else {
      if $mac_from_vrouter {
        $dpdk_dev_mac = $mac_from_vrouter
      } else {
        $dpdk_dev_mac = $dev_mac
      }
    }

    # in case of bonds, MAC address should be set permanently, because slave interfaces
    # may start in random order during the boot process
    if ( 'bond' in $raw_phys_dev) {
      file_line { 'permanent_mac':
        ensure => present,
        line => "hwaddress ${dpdk_dev_mac}",
        path => "/etc/network/interfaces.d/ifcfg-${raw_phys_dev}",
        after => "iface ${raw_phys_dev} inet manual",
      }
    }

    $install_packages = ['contrail-openstack-vrouter','contrail-vrouter-dpdk-init','iproute2','haproxy','libatm1']
    $delete_packages  = ['openvswitch-common','openvswitch-datapath-dkms','openvswitch-datapath-lts-saucy-dkms','openvswitch-switch','nova-network','nova-api']

    contrail_vrouter_dpdk_ini_config {
      'program:contrail-vrouter-dpdk/command':                 value => "taskset ${contrail::vrouter_core_mask} /usr/bin/contrail-vrouter-dpdk --no-daemon ${::supervisor_params}";
      'program:contrail-vrouter-dpdk/priority':                value => '410';
      'program:contrail-vrouter-dpdk/loglevel':                value => 'debug';
      'program:contrail-vrouter-dpdk/autostart':               value => true;
      'program:contrail-vrouter-dpdk/killasgroup':             value => true;
      'program:contrail-vrouter-dpdk/stdout_capture_maxbytes': value => '1MB';
      'program:contrail-vrouter-dpdk/redirect_stderr':         value => true;
      'program:contrail-vrouter-dpdk/stdout_logfile':          value => '/var/log/contrail/contrail-vrouter-dpdk-stdout.log';
      'program:contrail-vrouter-dpdk/stderr_logfile':          value => '/var/log/contrail/contrail-vrouter-dpdk-stderr.log';
      'program:contrail-vrouter-dpdk/exitcodes':               value => '0';
    }

    ini_subsetting {'vr_mpls_labels':
      ensure               => present,
      section              => 'program:contrail-vrouter-dpdk',
      key_val_separator    => '=',
      path                 => '/etc/contrail/supervisord_vrouter_files/contrail-vrouter-dpdk.ini',
      setting              => 'command',
      subsetting           => "--vr_mpls_labels=${contrail::vr_mpls_labels}",
      tag                  => 'vrouter_subsetting',
      subsetting_separator => ' ',
    }

    ini_subsetting {'vr_flow_entries':
      ensure               => present,
      section              => 'program:contrail-vrouter-dpdk',
      key_val_separator    => '=',
      path                 => '/etc/contrail/supervisord_vrouter_files/contrail-vrouter-dpdk.ini',
      setting              => 'command',
      subsetting           => "--vr_flow_entries=${contrail::vr_flow_entries}",
      tag                  => 'vrouter_subsetting',
      subsetting_separator => ' ',
    }

    Package[$install_packages] -> Contrail_vrouter_dpdk_ini_config <||> ~> Service['supervisor-vrouter']
    Contrail_vrouter_dpdk_ini_config <||> ->  Ini_subsetting <| tag == 'vrouter_subsetting' |> ~> Service['supervisor-vrouter']

  } else {
    $install_packages = ['contrail-openstack-vrouter','contrail-vrouter-dkms','iproute2','haproxy','libatm1']
    $delete_packages  = ['openvswitch-common','openvswitch-datapath-dkms','openvswitch-datapath-lts-saucy-dkms','openvswitch-switch','nova-network','nova-api']

    file {'/etc/modprobe.d/vrouter.conf':
      ensure  => present,
    }

    augeas { 'vrouter':
      context => '/files/etc/modprobe.d/vrouter.conf',
      lens    => 'modprobe.lns',
      incl    => '/etc/modprobe.d/vrouter.conf',
      changes => ["set options[. = 'vrouter'] vrouter",
                  "set options[. = 'vrouter']/vr_flow_entries ${contrail::vr_flow_entries}"],
      require => File['/etc/modprobe.d/vrouter.conf'],
    }
  }

  file { 'create_supervisor_vrouter_override':
    ensure  => present,
    path    => '/etc/init/supervisor-vrouter.override',
    content => 'manual',
  } ->
  package { $delete_packages:
    ensure => purged,
    tag    => ['delete'],
  } ->
  package { $install_packages:
    ensure => present,
    tag    => ['install'],
  } ->
  exec { 'remove-ovs-modules':
    command => 'modprobe -r openvswitch'
  } ->
  file {'/etc/contrail/agent_param':
    ensure  => present,
    content => template('contrail/agent_param.erb'),
    require => Package[$install_packages],
  } ->

  contrail_vrouter_nodemgr_config {
    'DISCOVERY/server': value => $contrail::contrail_private_vip;
    'DISCOVERY/port':   value => '5998';
  } ->

  exec { 'remove_supervisor_override':
    command => '/bin/rm /etc/init/supervisor-vrouter.override',
    onlyif  => '/usr/bin/test -f /etc/init/supervisor-vrouter.override',
    require => Package[$install_packages],
  }

  contrail_vrouter_agent_config {
    'DEFAULT/log_file':                          value => '/var/log/contrail/contrail-vrouter-agent.log';
    'DEFAULT/log_level':                         value => 'SYS_NOTICE';
    'DEFAULT/log_local':                         value => '1';
    'DEFAULT/log_flow':                          value => '1';
    'DEFAULT/use_syslog':                        value => '1';
    'DEFAULT/syslog_facility':                   value => 'LOG_LOCAL0';
    'DEFAULT/headless_mode':                     value => $::contrail::headless_mode;
    'DISCOVERY/server':                          value => $::contrail::contrail_private_vip;
    'DISCOVERY/max_control_nodes':               value => '2';
    'HYPERVISOR/type':                           value => 'kvm';
    'METADATA/metadata_proxy_secret':            value => $::contrail::metadata_secret;
    'NETWORKS/control_network_ip':               value => $::contrail::address;
    'VIRTUAL-HOST-INTERFACE/name':               value => 'vhost0';
    'VIRTUAL-HOST-INTERFACE/ip':                 value => "${contrail::address}/${contrail::netmask_short}";
    'VIRTUAL-HOST-INTERFACE/physical_interface': value => $phys_dev;
    'SERVICE-INSTANCE/netns_command':            value => '/usr/bin/opencontrail-vrouter-netns';
  }

  if $contrail::gateway {
    contrail_vrouter_agent_config { 'VIRTUAL-HOST-INTERFACE/gateway': value => $contrail::gateway; }
  }

  if $contrail::compute_dpdk_enabled == true {
    contrail_vrouter_agent_config {
      'DEFAULT/platform':                    value => 'dpdk';
      'DEFAULT/physical_interface_address' : value => $dpdk_dev_pci;
      'DEFAULT/physical_interface_mac':      value => $dpdk_dev_mac;
    }
    file {'/etc/network/interfaces.d/ifcfg-vhost0':
      ensure  => present,
      content => template('contrail/ubuntu-ifcfg-vhost0.erb'),
    } ~>
    service {'supervisor-vrouter':
      ensure    => running,
      enable    => true,
    }
  } else {
    contrail_vrouter_agent_config {
      'TASK/thread_count':  value => '8';
      'FLOWS/thread_count': value => $contrail::vrouter_thread_count;
    }
    file {'/etc/network/interfaces.d/ifcfg-vhost0':
      ensure  => present,
      content => template('contrail/ubuntu-ifcfg-vhost0.erb'),
    } ~>
    service {'supervisor-vrouter':
      ensure     => running,
      enable     => true,
      hasrestart => false,
      restart    => 'service supervisor-vrouter stop && \
modprobe -r vrouter && \
sync && \
echo 3 > /proc/sys/vm/drop_caches && \
echo 1 > /proc/sys/vm/compact_memory && \
service supervisor-vrouter start',
    }
  }
  Package[$install_packages] -> Contrail_vrouter_nodemgr_config <||> ~> Service['supervisor-vrouter']
  Package[$install_packages] -> Contrail_vrouter_agent_config <||>   ~> Service['supervisor-vrouter']
}
