class contrail::service ( $node_role ) {

  case $node_role {
    'base-os': {
      $services = $operatingsystem ? {
        'Ubuntu' => ['haproxy','keepalived','neutron-server','supervisor-support-service','redis-server'],
        default  => undef,
      }
    }
    'controller','primary_controller': {
      $services = $operatingsystem ? {
        'Ubuntu' => ['nova-api','nova-scheduler','nova-conductor'],
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
