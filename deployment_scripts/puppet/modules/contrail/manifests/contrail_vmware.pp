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

  if $contrail::use_vcenter {

    $cfgm_ip                 = $contrail::contrail_private_vip
    $ncontrols               = size($contrail::contrail_control_ips)
    $amqp_server_ip          = $contrail::contrail_private_vip
    $service_token           = $contrail::admin_token
    $hypervisor              = $contrail::hypervisor
    $keystone_ip             = $contrail::mos_mgmt_vip
    $keystone_admin_user     = $contrail::neutron_user
    $keystone_admin_password = $contrail::service_token
    $service_tenant_name     = $contrail::service_tenant
    $internal_vip            = $contrail::mos_mgmt_vip
    $external_vip            = $contrail::mos_public_vip
    $contrail_internal_vip   = $contrail::contrail_private_vip
    $dev_mac                 = $contrail::dev_mac
    $mgmt_self_ip            = $::ipaddress_br_mgmt

    # Fetching the esxi data from hash
    $mapping_data            = loadyaml('/etc/hiera/plugins/contrail-esxi-vrouter-map.yaml')
    $host_to_mac_bind        = loadyaml('/etc/hiera/plugins/contrail-host-to-mac-bind.yaml')
    $host                    = pick($mapping_data['esxi_mapping'][$contrail::address], '')
    $esxi_dvs_mac_list       = pick($host_to_mac_bind['contrail_host_to_mac_binding'][$host], '')
    $if_names                = interface_name_by_mac($esxi_dvs_mac_list)
    $vmware_iface_name       = pick($if_names['0'], 'ens162')

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

    file { 'create_supervisor_vrouter_override':
      ensure  => present,
      path    => '/etc/init/supervisor-vrouter.override',
      content => 'manual',
    }

    if !defined(File['/var/crashes']) {
      file {'/var/crashes':
        ensure => directory,
        mode   => '1777',
        before => File_line['use_kdump'],
      }
    }

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
    } ->
    contrail_vrouter_agent_config {
      'DEFAULT/platform'                          : value => 'default';
      'DEFAULT/physical_interface_address'        : value => $contrail::phys_dev_pci;
      'DEFAULT/physical_interface_mac'            : value => $dev_mac;
      'DEFAULT/log_file'                          : value => '/var/log/contrail/contrail-vrouter-agent.log';
      'DEFAULT/log_level'                         : value => $contrail::log_level;
      'DEFAULT/log_local'                         : value => '1';
      'DEFAULT/log_flow'                          : value => $contrail::log_flow;
      'DEFAULT/use_syslog'                        : value => $contrail::use_syslog;
      'DEFAULT/syslog_facility'                   : value => $contrail::syslog_facility;
      'DEFAULT/headless_mode'                     : value => true;
      'DISCOVERY/server'                          : value => $contrail::contrail_private_vip;
      'DISCOVERY/max_control_nodes'               : value => '2';
      'HYPERVISOR/type'                           : value => 'vmware';
      'HYPERVISOR/vmware_mode'                    : value => 'vcenter';
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
    }
    #NOTE(AKirilochkin): This configuration will be passed until "interface_name_by_mac"
    # function could not get the data from hash. We do not need LCM rewrite this empty data.
    if $if_names['0'] {
      contrail_vrouter_agent_config {
        'HYPERVISOR/vmware_physical_interface'      : value => $vmware_iface_name;
      }
    }

    # VNC API
    if !defined(File['/etc/contrail/vnc_api_lib.ini']) {
      file { '/etc/contrail/vnc_api_lib.ini':
        content => template('contrail/vnc_api_lib.ini.erb'),
      }
    }

    service {'supervisor-vrouter':
      ensure    => running,
      enable    => true,
      subscribe => [Exec['remove-ovs-modules'],
                    File['/etc/contrail/agent_param']],
    } ->
    exec { 'register_contrailvm_vrouter':
      path    => '/usr/local/bin:/bin:/usr/bin/',
      cwd     => '/opt/contrail/utils',
      command => "python provision_vrouter.py --host_name ${::fqdn} --host_ip ${contrail::address} \
--api_server_ip ${contrail_internal_vip} --api_server_port ${contrail::api_server_port} \
--oper add --admin_user ${keystone_admin_user} --admin_password ${keystone_admin_password} \
--admin_tenant_name ${service_tenant_name} --openstack_ip ${contrail::internal_auth_address} \
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
