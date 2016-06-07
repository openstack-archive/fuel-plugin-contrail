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

  if $contrail::use_vcenter and $contrail::provision_vmware_type == 'fuel'{

    $self_ip = $contrail::address
    $cfgm_ip = $contrail::contrail_private_vip

    $ncontrols               = size($contrail::contrail_control_ips)
    $amqp_server_ip          = $contrail::contrail_private_vip
    $service_token           = $contrail::admin_token
    $orchestrator            = $contrail::orchestrator
    $hypervisor              = $contrail::hypervisor
    $keystone_ip             = $contrail::mos_mgmt_vip
    $keystone_admin_user     = $contrail::neutron_user
    $keystone_admin_password = $contrail::service_token
    $service_tenant_name     = $contrail::service_tenant
    $internal_vip            = $contrail::mos_mgmt_vip
    $external_vip            = $contrail::mos_public_vip
    $contrail_internal_vip   = $contrail::contrail_private_vip
    $mgmt_self_ip            = $::ipaddress_br_mgmt

    # Fetching the esxi data from hash
    $esxi_data               = fetch_esxi_data("root@${self_ip}")
    $vmware                  = $esxi_data['ip']
    $vmware_username         = $esxi_data['username']
    $vmware_passwd           = $esxi_data['password']
    $vmware_iface_name       = $esxi_data['contrail_vm']['vmware_iface_name']
    $vmware_vmpg_vswitch     = $esxi_data['fabric_vswitch']
    $vmware_vmpg_vswitch_mtu = '9000'
    $mode                    = $contrail::mode
    $contrailvm_ntp          = $contrail::contrailvm_ntp

    $phys_dev_facter = regsubst($::contrail::phys_dev, '\.' , '_')
    $dev_mac         = getvar("::macaddress_${phys_dev_facter}")

    $delete_packages  = ['openvswitch-common', 'openvswitch-datapath-dkms',
      'openvswitch-datapath-lts-saucy-dkms', 'openvswitch-switch', 'nova-network',
      'nova-api']
    $install_packages = ['contrail-install-packages', 'contrail-fabric-utils',
      'contrail-setup', 'contrail-vrouter-dkms', 'contrail-vrouter-common',
      'contrail-nova-vif', 'open-vm-tools', 'iproute2']

    l23network::l3::ifconfig { $vmware_iface_name: ipaddr => 'none' }

    $sysctl_settings = {
      'net.nf_conntrack_max'             => { value => '1048576'},
      'kernel.panic'                     => { value => '60'},
      'net.ipv4.conf.default.arp_accept' => { value => '1'},
      'net.core.netdev_max_backlog'      => { value => '261144'},
      'net.ipv4.tcp_keepalive_intvl'     => { value => '3'},
      'net.ipv4.tcp_keepalive_time'      => { value => '30'},
      'net.ipv4.tcp_keepalive_probes'    => { value => '8'},
      'net.ipv4.conf.all.arp_accept'     => { value => '1'},
      'net.ipv4.tcp_retries2'            => { value => '5'},
      'net.ipv4.conf.all.rp_filter'      => { value => '2'},
      'net.ipv4.conf.default.rp_filter'  => { value => '2'},
      'kernel.core_pattern'              => { value => '/var/crashes/core.%e.%p.%h.%t'},
    }

    $sysctl_defaults = {
      require => File['/var/crashes'],
    }

    create_resources(sysctl::value, $sysctl_settings, $sysctl_defaults)

    file_line { 'kexec-tools':
      path  => '/etc/default/kdump-tools',
      match => 'crashkernel=.*\([ | \"]\)',
      line  => 'crashkernel=384M-2G:64M,2G-16G:128M,16G-:256M\1',
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

    file {'/var/crashes':
      ensure => directory,
      mode   => '1777',
    } ->

    file_line { 'use_kdump':
      path  => '/etc/default/kdump-tools',
      match => 'USE_KDUMP=.*',
      line  => 'USE_KDUMP=1',
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
      'HYPERVISOR/vmware_physical_interface'      : value => $vmware_iface_name;
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
    exec { 'remove_supervisor_override':
      command => '/bin/rm /etc/init/supervisor-vrouter.override',
      onlyif  => '/usr/bin/test -f /etc/init/supervisor-vrouter.override',
      require => Class['Contrail::Package'],
    }

    service {'supervisor-vrouter':
      ensure    => running,
      enable    => true,
      subscribe => [Class[Contrail::Package],
                    Exec['remove-ovs-modules'],
                    File['/etc/contrail/agent_param']],
    } ->
    exec { 'register_contrailvm_vrouter':
      path    => '/usr/local/bin:/bin:/usr/bin/',
      cwd     => '/opt/contrail/utils',
      command => "python provision_vrouter.py --host_name ${::fqdn} --host_ip ${self_ip} \
--api_server_ip ${contrail_internal_vip} --api_server_port ${contrail::api_server_port} \
--oper add --admin_user ${keystone_admin_user} --admin_password ${keystone_admin_password} \
--admin_tenant_name ${service_tenant_name} --openstack_ip ${internal_vip} \
&& touch /opt/contrail/register_contrailvm_vrouter-DONE",
      creates => '/opt/contrail/register_contrailvm_vrouter-DONE',
    }
    exec {'command when file not exists':
      command => 'touch /tmp/contrail-reboot-require && touch /opt/contrail/reboot-DONE',
      onlyif  => 'test ! -f /opt/contrail/reboot-DONE',
      path    => ['/usr/bin','/usr/sbin','/bin','/sbin'],
    }
    Contrail_vrouter_nodemgr_config <||> ~> Service['supervisor-vrouter']
    Contrail_vrouter_agent_config   <||> ~> Service['supervisor-vrouter']
  }
}
