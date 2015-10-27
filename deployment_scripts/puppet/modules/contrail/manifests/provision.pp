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

class contrail::provision ( $node_role ) {

  Exec {
    provider => 'shell',
    path     => '/usr/bin:/bin:/sbin',
  }

  $gateways = split($contrail::settings['contrail_gateways'], ',')

  define contrail::provision::prov_ext_bgp {
    exec { "prov_external_bgp_${name}":
      command  => "python /opt/contrail/utils/provision_mx.py  \
--api_server_ip ${contrail::contrail_mgmt_vip} --api_server_port 8082 \
--oper add --router_name ${name} --router_ip ${name} \
--admin_user neutron --admin_tenant_name services --admin_password ${contrail::service_token} \
&& touch /opt/contrail/prov_external_bgp_${name}-DONE",
      creates  => "/opt/contrail/prov_external_bgp_${name}-DONE",
    }
  }

  case $node_role {
    'base-os': {
      notify {'Waiting for contrail API':} ->
      exec {'wait_for_api':
        command    => "if [ `curl --silent --output /dev/null --write-out \"%{http_code}\" http://${contrail::contrail_mgmt_vip}:8082` -lt 401 ];\
then exit 1; fi",
        tries     => 10,
        try_sleep => 10,
      } ->
      exec { 'prov_control_bgp':
        command  => "python /opt/contrail/utils/provision_control.py \
--api_server_ip ${contrail::contrail_mgmt_vip} --api_server_port 8082 \
--oper add --host_name ${::fqdn} --host_ip ${contrail::address} --router_asn ${contrail::asnum} \
--admin_user neutron --admin_tenant_name services --admin_password ${contrail::service_token} \
&& touch /opt/contrail/prov_control_bgp-DONE",
        require  => Exec['wait_for_api'],
        creates  => '/opt/contrail/prov_control_bgp-DONE',
      }
      if $contrail::node_name == $contrail::deployment_node {
        contrail::provision::prov_ext_bgp { $gateways:
          require  => [Exec['wait_for_api'],Exec['prov_control_bgp']],
        } ->
        exec { 'prov_metadata_services':
          command  => "python /opt/contrail/utils/provision_linklocal.py \
--api_server_ip ${contrail::contrail_mgmt_vip} --api_server_port 8082 \
--oper add \
--linklocal_service_name metadata --linklocal_service_ip 169.254.169.254 --linklocal_service_port 80 \
--ipfabric_service_ip ${contrail::mos_mgmt_vip} --ipfabric_service_port 8775  \
--admin_user neutron --admin_tenant_name services --admin_password ${contrail::service_token} \
&& touch /opt/contrail/prov_metadata_service-DONE",
          require  => Exec['wait_for_api'],
          creates  => '/opt/contrail/prov_metadata_service-DONE',
        } ->
        exec { 'prov_encap_type':
          command  => "python /opt/contrail/utils/provision_encap.py \
--api_server_ip ${contrail::contrail_mgmt_vip} --api_server_port 8082 \
--oper add --encap_priority MPLSoUDP,MPLSoGRE,VXLAN \
--admin_user ${contrail::admin_username} --admin_password ${contrail::admin_password} \
&& touch /opt/contrail/prov_encap_type-DONE",
          require  => Exec['wait_for_api'],
          creates  => '/opt/contrail/prov_encap_type-DONE',
        }
      }
    }
    'controller': {
      file {'/etc/hiera/override': ensure => directory } ->
      file {'/etc/hiera/override/plugins.yaml':
        ensure  => present,
        content => template('contrail/plugins.yaml.erb'),
      }
      if hiera('primary_controller') and $contrail::nets and !empty($contrail::nets) {
        contrail::create_network{'net04':
          netdata           => $contrail::nets['net04'],
          require           => File['/etc/hiera/override/plugins.yaml'],
        } ->
        contrail::create_network{'net04_ext':
          netdata           => $contrail::nets['net04_ext'],
          notify            => Exec['prov_route_target'],
        } ->
        openstack::network::create_router{'router04':
          internal_network  => 'net04',
          external_network  => 'net04_ext',
          tenant_name       => $contrail::admin_tenant
        }
        exec { 'prov_route_target':
          command => "python /opt/contrail/utils/add_route_target.py \
--routing_instance_name default-domain:${contrail::admin_tenant}:net04_ext:net04_ext \
--route_target_number ${contrail::route_target} --router_asn ${contrail::asnum} \
--api_server_ip ${contrail::contrail_mgmt_vip} --api_server_port 8082 \
--admin_user neutron --admin_tenant_name services --admin_password ${contrail::service_token} \
&& touch /opt/contrail/prov_route_target-DONE",
          creates => '/opt/contrail/prov_route_target-DONE',
          require => Contrail::Create_Network['net04_ext'],
        }
      }
    }
    'compute': {
      exec { 'provision-vrouter':
        path    => '/bin:/usr/bin/',
        command => "python /opt/contrail/utils/provision_vrouter.py \
--api_server_ip ${contrail::contrail_mgmt_vip} --api_server_port 8082 --openstack_ip ${contrail::mos_mgmt_vip} \
--oper add --host_name ${::fqdn} --host_ip ${contrail::address} \
--admin_user neutron --admin_tenant_name services --admin_password ${contrail::service_token} \
&& touch /opt/contrail/provision-vrouter-DONE",
        creates => '/opt/contrail/provision-vrouter-DONE',
      }
    }
    default: {}
  }

}

