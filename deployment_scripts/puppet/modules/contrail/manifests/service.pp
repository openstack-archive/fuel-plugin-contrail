class contrail::service ( $node_role ) {

  case $node_role {
    'base-os': {
      $services = $operatingsystem ? {
        ubuntu  => ['haproxy','keepalived','neutron-server'],
        default => undef,
      }
    }
    'controller','primary_controller': {
      $services = $operatingsystem ? {
        ubuntu  => ['nova-api','nova-scheduler','nova-conductor'],
        default => undef,
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
