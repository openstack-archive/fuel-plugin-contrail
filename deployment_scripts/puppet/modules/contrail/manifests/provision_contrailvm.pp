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


define contrail::provision_contrailvm (
  $host = split($title, '@'),
  )
{

  $self_ip = $host[1]
  $cfgm_ip = $contrail::contrail_private_vip
  $ncontrols = size($contrail::contrail_control_ips)
  $amqp_server_ip = $contrail::contrail_private_vip
  $service_token = $contrail::admin_token
  $orchestrator = 'openstack'
  $hypervisor = 'libvirt'
  $keystone_ip = $contrail::mos_mgmt_vip
  #$openstack_mgmt_ip
  $keystone_auth_protocol = 'http'
  $keystone_auth_port = '35357'
  $quantum_service_protocol = 'http'
  $keystone_admin_user = 'neutron'
  $keystone_admin_password = $contrail::service_token
  #$nova_password admin
  #$neutron_password
  $service_tenant_name = 'services'
  $internal_vip = $contrail::mos_mgmt_vip
  $external_vip = $contrail::mos_public_vip
  $contrail_internal_vip = $contrail::contrail_private_vip
  $mgmt_self_ip = $host[1]
  $esxi_data = fetch_esxi_data($title)
  $vmware = $esxi_data['ip']
  $vmware_username = $esxi_data['username']
  $vmware_passwd = $esxi_data['password']
  $vmware_vmpg_vswitch = $esxi_data['fabric_vswitch']
  $vmware_vmpg_vswitch_mtu = '9000'
  $mode = 'vcenter'
  $oktets = split($self_ip, '\.')
  $last_oktet = $oktets[3]
  $vm_hostname = "ContrailVM-${last_oktet}"
  $contrailvm_ntp = $contrail::contrailvm_ntp

  $provisioning_cmd = "setup-vnc-compute --self_ip ${self_ip} \
  --cfgm_ip ${cfgm_ip} \
  --ncontrols ${ncontrols} \
  --amqp_server_ip ${amqp_server_ip} \
  --service_token ${service_token} \
  --orchestrator ${orchestrator}  \
  --hypervisor ${hypervisor} \
  --keystone_ip ${keystone_ip} \
  --keystone_auth_protocol ${keystone_auth_protocol} \
  --keystone_auth_port ${keystone_auth_port} \
  --quantum_service_protocol ${quantum_service_protocol} \
  --keystone_admin_user ${keystone_admin_user} \
  --keystone_admin_password ${keystone_admin_password} \
  --service_tenant_name ${service_tenant_name} \
  --internal_vip ${internal_vip} \
  --external_vip ${external_vip} \
  --no_contrail_openstack \
  --no_nova_config \
  --contrail_internal_vip ${contrail_internal_vip} \
  --mgmt_self_ip ${mgmt_self_ip} \
  --vmware ${vmware} \
  --vmware_username ${vmware_username} \
  --vmware_passwd ${vmware_passwd} \
  --vmware_vmpg_vswitch ${vmware_vmpg_vswitch} \
  --vmware_vmpg_vswitch_mtu ${vmware_vmpg_vswitch_mtu} \
  --mode ${mode}"

  $register_cmd = "python provision_vrouter.py --host_name ${vm_hostname} \
  --host_ip ${self_ip} \
  --api_server_ip ${contrail_internal_vip} \
  --oper add \
  --admin_user ${keystone_admin_user} \
  --admin_password ${keystone_admin_password} \
  --admin_tenant_name ${service_tenant_name} \
  --openstack_ip ${internal_vip}"

  exec { "disable_add_vnc_config-${self_ip}":
    path    => '/usr/local/bin:/bin:/usr/bin/',
    cwd     => '/opt/contrail/utils',
    command => "fab -H ${title} disable_add_vnc_config && touch /opt/contrail/disable_add_vnc_config-${self_ip}-DONE",
    creates => "/opt/contrail/disable_add_vnc_config-${self_ip}-DONE",
  } ->

  exec { "change_hostname-${self_ip}":
    path    => '/usr/local/bin:/bin:/usr/bin/',
    cwd     => '/opt/contrail/utils',
    command => "fab -H ${title} change_hostname:'${vm_hostname}' && touch /opt/contrail/change_hostname-${self_ip}-DONE",
    creates => "/opt/contrail/change_hostname-${self_ip}-DONE",
  } ->

  exec { "deploy_agent_param_${self_ip}":
    path      => '/usr/local/bin:/bin:/usr/bin/',
    cwd       => '/opt/contrail/utils',
    command   => "fab -H ${title} deploy_agent_param && touch /opt/contrail/fab_deploy_agent_param-${self_ip}-DONE",
    creates   => '/opt/contrail/fab_deploy_agent_param-${self_ip}-DONE',
   } ->

  exec { "redeploy_vrouter_module_${self_ip}":
    path      => '/usr/local/bin:/bin:/usr/bin/',
    cwd       => '/opt/contrail/utils',
    command   => "fab -H ${title} redeploy_vrouter_module && touch /opt/contrail/fab_redeploy_vrouter_module-${self_ip}-DONE",
    creates   => '/opt/contrail/fab_redeploy_vrouter_module-${self_ip}-DONE',
   } ->

  exec{ "set_ntp-${self_ip}":
    path    => '/usr/local/bin:/bin:/usr/bin/',
    cwd     => '/opt/contrail/utils',
    command => "fab -H ${title} set_ntp:'${contrailvm_ntp}' && touch /opt/contrail/set_ntp-${self_ip}-DONE",
    creates => "/opt/contrail/set_ntp-${self_ip}-DONE",
  } ->

  exec { "provision_contrailvm-${self_ip}":
    path    => '/usr/local/bin:/bin:/usr/bin/',
    cwd     => '/opt/contrail/utils',
    command => "fab -H ${title} provision_contrailvm:'${provisioning_cmd}' && touch /opt/contrail/provision_contrailvm-${self_ip}-DONE",
    creates => "/opt/contrail/provision_contrailvm-${self_ip}-DONE",
  } ->

  exec { "register_contrailvm_vrouter-${self_ip}":
    path    => '/usr/local/bin:/bin:/usr/bin/',
    cwd     => '/opt/contrail/utils',
    command => "${register_cmd} && touch /opt/contrail/register_contrailvm_vrouter-${self_ip}-DONE",
    creates => "/opt/contrail/register_contrailvm_vrouter-${self_ip}-DONE",
  } ->

  exec { "reboot_contrailvm-${self_ip}":
    path    => '/usr/local/bin:/bin:/usr/bin/',
    cwd     => '/opt/contrail/utils',
    command => "fab -H ${title} provision_contrailvm:'reboot' && touch /opt/contrail/reboot_contrailvm-${self_ip}-DONE",
    creates => "/opt/contrail/reboot_contrailvm-${self_ip}-DONE",
  }
}
