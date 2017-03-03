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

  $raw_phys_dev = $contrail::raw_phys_dev

  if $contrail::compute_dpdk_enabled {

    if !defined(File['/var/crashes']) {
      file { '/var/crashes':
        ensure => directory,
        mode   => '1777',
      }
    }

    # in case of bonds, MAC address should be set permanently, because slave interfaces
    # may start in random order during the boot process
    if ( 'bond' in $raw_phys_dev) {
      file_line { 'permanent_mac':
        ensure => present,
        line   => "hwaddress ${::dpdk_mac_address}",
        path   => "/etc/network/interfaces.d/ifcfg-${raw_phys_dev}",
        after  => "iface ${raw_phys_dev} inet manual",
      }
    }

    $install_packages = ['contrail-openstack-vrouter','contrail-vrouter-dpdk-init','iproute2','haproxy','libatm1']
    $delete_packages  = ['openvswitch-common','openvswitch-datapath-dkms','openvswitch-datapath-lts-saucy-dkms','openvswitch-switch','nova-network','nova-api']

    contrail_vrouter_dpdk_ini_config {
      'program:contrail-vrouter-dpdk/command':                 value => "${contrail::taskset_command} /usr/bin/contrail-vrouter-dpdk --no-daemon ${::supervisor_params}";
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

    Class[Contrail::Package] -> Contrail_vrouter_dpdk_ini_config <||> ~> Service['supervisor-vrouter']
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

  if !is_pkg_installed('contrail-openstack-vrouter') {
    file { 'create_supervisor_vrouter_override':
      ensure  => present,
      path    => '/etc/init/supervisor-vrouter.override',
      content => 'manual',
      before  => Class['contrail::package'],
    }
  }

  if !defined(File['/var/crashes']) {
    file { '/var/crashes':
      ensure  => directory,
      mode    => '0777',
      before  => Class['contrail::package'],
    }
  }

  class { 'contrail::package':
    install => [$install_packages],
    remove  => [$delete_packages],
  } ->
  exec { 'remove-ovs-modules':
    command => '/sbin/modprobe -r openvswitch',
    onlyif  => '/sbin/lsmod | grep -q ^openvswitch',
  } ->
  file {'/etc/contrail/agent_param':
    ensure  => present,
    content => template('contrail/agent_param.erb'),
    require => Class[Contrail::Package],
  } ->

  contrail_vrouter_agent_config {
    'DEFAULT/log_file':                          value => '/var/log/contrail/contrail-vrouter-agent.log';
    'DEFAULT/log_level':                         value => $contrail::log_level;
    'DEFAULT/log_local':                         value => '1';
    'DEFAULT/log_flow':                          value => $contrail::log_flow;
    'DEFAULT/use_syslog':                        value => $contrail::use_syslog;
    'DEFAULT/syslog_facility':                   value => $contrail::syslog_facility;
    'DEFAULT/headless_mode':                     value => $contrail::headless_mode;
    'DISCOVERY/server':                          value => $contrail::contrail_private_vip;
    'DISCOVERY/max_control_nodes':               value => '2';
    'HYPERVISOR/type':                           value => 'kvm';
    'METADATA/metadata_proxy_secret':            value => $contrail::metadata_secret;
    'NETWORKS/control_network_ip':               value => $contrail::address;
    'VIRTUAL-HOST-INTERFACE/name':               value => 'vhost0';
    'VIRTUAL-HOST-INTERFACE/ip':                 value => "${contrail::address}/${contrail::netmask_short}";
    'VIRTUAL-HOST-INTERFACE/physical_interface': value => $contrail::phys_dev;
    'SERVICE-INSTANCE/netns_command':            value => '/usr/bin/opencontrail-vrouter-netns';
  }

  file { '/etc/contrail/supervisord_vrouter.conf.erb':
    content => template('contrail/supervisord_vrouter.conf.erb'),
    require => Class[Contrail::Package],
  }

  if $::contrail::tls_xmpp_enable {

    file { '/etc/contrail/ssl/':
      ensure => directory,
      owner  => 'contrail',
      group  => 'contrail',
      tag    => 'tls_xmpp',
    }

    file { '/etc/contrail/ssl/xmpp_wildcard.crt':
      content  => $contrail::tls_xmpp_wildcard_crt,
      owner    => 'contrail',
      group    => 'contrail',
      tag      => 'tls_xmpp',
    }

    file { '/etc/contrail/ssl/xmpp_wildcard.key':
      content  => $contrail::tls_xmpp_wildcard_key,
      owner    => 'contrail',
      group    => 'contrail',
      tag      => 'tls_xmpp',
    }

    file { '/etc/contrail/ssl/xmpp_ca.crt':
      content  => $contrail::tls_xmpp_ca_crt,
      owner    => 'contrail',
      group    => 'contrail',
      tag      => 'tls_xmpp',
    }

    contrail_vrouter_agent_config {
      'DEFAULT/xmpp_auth_enable': value => true;
      'DEFAULT/xmpp_dns_auth_enable': value => true;
      'DEFAULT/xmpp_server_cert': value => '/etc/contrail/ssl/xmpp_wildcard.crt';
      'DEFAULT/xmpp_server_key':  value => '/etc/contrail/ssl/xmpp_wildcard.key';
      'DEFAULT/xmpp_ca_cert':     value => '/etc/contrail/ssl/xmpp_ca.crt';
    }

    Package[$install_packages] -> File<| tag == 'tls_xmpp' |>  -> Contrail_vrouter_agent_config <||>  ~> Service['supervisor-vrouter']

  }
  if $contrail::gateway {
    contrail_vrouter_agent_config { 'VIRTUAL-HOST-INTERFACE/gateway': value => $contrail::gateway; }
  }

  if $contrail::compute_dpdk_enabled == true {
    contrail_vrouter_agent_config {
      'DEFAULT/platform':                    value => 'dpdk';
      'DEFAULT/physical_interface_address' : value => $contrail::phys_dev_pci;
      'DEFAULT/physical_interface_mac':      value => $::dpdk_mac_address;
    }
  } else {
    contrail_vrouter_agent_config {
      'TASK/thread_count':                   value => '8';
      'FLOWS/thread_count':                  value => '2';
    }
  }

  contrail_vrouter_nodemgr_config {
    'DISCOVERY/server': value => $contrail::contrail_private_vip;
    'DISCOVERY/port':   value => '5998';
  } ->

  exec { 'remove_supervisor_override':
    command => '/bin/rm /etc/init/supervisor-vrouter.override',
    onlyif  => '/usr/bin/test -f /etc/init/supervisor-vrouter.override',
    require => Class['Contrail::Package'],
  } ->
  service {'supervisor-vrouter':
    ensure    => running,
    enable    => true,
    subscribe => [
      Class[Contrail::Package],
      Exec['remove-ovs-modules'],
      File['/etc/contrail/agent_param'],
      File['/etc/contrail/supervisord_vrouter.conf.erb'],
      ],
  }
  Contrail_vrouter_nodemgr_config <||> ~> Service['supervisor-vrouter']
  Contrail_vrouter_agent_config <||>   ~> Service['supervisor-vrouter']
}
