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
    path     => '/usr/bin:/bin',
  }

  $gateways = split($contrail::settings['contrail_gateways'], ',')

  define contrail::provision::prov_ext_bgp {
    exec { 'prov_external_bgp_${name}':
      command  => "python /opt/contrail/utils/provision_mx.py --router_name mx1 --router_ip ${name} --api_server_ip ${contrail::contrail_mgmt_vip} --api_server_port 8082 --oper add && touch /opt/contrail/prov_external_bgp_${name}-DONE",
      creates  => "/opt/contrail/prov_external_bgp_prov_external_bgp_${name}-DONE",
    }
  }

  case $node_role {
    'base-os': {
      notify {'Waiting for contrail API':} ->
      exec {'wait_for_api':
        command   => "while [ 200 != $(curl --silent --output /dev/null --write-out \"%{http_code}\" http://${contrail::contrail_mgmt_vip}:8082) ]; do sleep 2; done",
        tries     => 10, # wait for api is up: 10 tries every 30 seconds = 5 min
        try_sleep => 30,
      } ->
      exec { 'prov_control_bgp':
        command  => "python /opt/contrail/utils/provision_control.py --api_server_ip ${contrail::contrail_mgmt_vip} --api_server_port 8082 --oper add --host_name ${::fqdn}  --host_ip ${contrail::address} --router_asn ${contrail::asnum} --admin_user ${contrail::admin_username} --admin_tenant_name services --admin_password  ${contrail::admin_password} && touch /opt/contrail/prov_control_bgp-DONE",
        require  => Exec['wait_for_api'],
        creates  => '/etc/contrail//opt/contrail/prov_control_bgp-DONE',
      }
      if $contrail::node_name == $contrail::deployment_node {
        contrail::provision::prov_ext_bgp { $gateways:
          require  => Exec['wait_for_api'],
        }
        exec { 'prov_metadata_services':
          command  => "python  /opt/contrail/utils/provision_linklocal.py --api_server_ip ${contrail::contrail_mgmt_vip} --api_server_port 8082 --linklocal_service_name metadata --linklocal_service_ip 169.254.169.254 --linklocal_service_port 80 --ipfabric_service_ip ${contrail::mos_mgmt_vip} --ipfabric_service_port 8775 --oper add --admin_user ${contrail::admin_username} --admin_tenant_name services --admin_password  ${contrail::admin_password} && touch /opt/contrail/prov_metadata_service-DONE",
          require  => Exec['wait_for_api'],
          creates  => '/opt/contrail/prov_metadata_service-DONE',
        }
        exec { 'prov_encap_type':
          command  => "python  /opt/contrail/utils/provision_encap.py --api_server_ip ${contrail::contrail_mgmt_vip}  --api_server_port 8082 --encap_priority MPLSoUDP,MPLSoGRE,VXLAN --oper add --admin_user ${contrail::admin_username} --admin_password ${contrail::admin_password} && touch /opt/contrail/prov_encap_type-DONE",
          require  => Exec['wait_for_api'],
          creates  => '/opt/contrail/prov_encap_type-DONE',
        }
      }
    }
    'controller','primary-controller': {
      keystone_endpoint {'RegionOne/neutron':
        ensure       => present,
        public_url   => "http://${contrail::contrail_mgmt_vip}:9696/",
        admin_url    => "http://${contrail::contrail_mgmt_vip}:9696/",
        internal_url => "http://${contrail::contrail_mgmt_vip}:9696/",
      }
    }
    'compute': {
      exec { 'provision-vrouter':
        path    => '/bin:/usr/bin/',
        command => "python /opt/contrail/utils/provision_vrouter.py --host_name ${::fqdn} \
--host_ip ${contrail::address} --api_server_ip ${contrail::contrail_mgmt_vip} --openstack_ip ${contrail::mos_mgmt_vip} \
--admin_user neutron --admin_password ${contrail::service_token} --admin_tenant_name services --oper add && touch /opt/contrail/provision-vrouter-DONE",
        creates => '/opt/contrail/provision-vrouter-DONE',
      }
    }
    default: {}
  }

}

