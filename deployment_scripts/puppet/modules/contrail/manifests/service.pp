class contrail::service ( $node_role ) {

  case $node_role {
    'base-os': {
      $services = $operatingsystem ? {
        'Ubuntu' => ['haproxy','keepalived','neutron-server','supervisor-support-service','redis-server','contrail-api'],
        'CentOS' => ['haproxy','keepalived','neutron-server','supervisor-support-service','redis','contrail-api'],
        default  => undef,
      }
    }
    'controller','primary-controller': {
      $services = $operatingsystem ? {
        'Ubuntu' => ['nova-api','nova-scheduler','nova-conductor'],
        'CentOS' => ['openstack-nova-api','openstack-nova-scheduler','openstack-nova-conductor'],
        default  => undef,
      }
    }
  }

  if ( $services ) {
    service { $services:
      ensure => running,
      enable => true,
    }
  }

}
