class contrail {

  $settings = hiera('contrail')
  $role = hiera('role')
  $node_name = hiera('user_node_name')

  case $role {
    /^.*controller$/: {
      class { contrail::packages:
        install => ['python-paramiko, contrail-fabric-utils, contrail-setup'],
      }
    }
    /^compute$/: {
      class { contrail::packages:
        install => 'contrail-openstack-vrouter',
        remove  => ['openvswitch-common','openvswitch-datapath-lts-saucy-dkms','openvswitch-switch',
                  'nova-network','nova-api'],
      }
    }
    /^base-os$/: {
      case $node_name {
        /^contrail.\d+$/: {
          class { contrail::packages:
            install => ['python-crypto','python-netaddr','python-paramiko',
            'contrail-fabric-utils','contrail-setup'],
            responsefile => 'contrail.preseed',
          }
        }
        default: {
          notify { "This is not a contrail controller node. Plugin tasks aborted": }
        }
      }
    }
  } 
  
} 
