include contrail
if $contrail::node_name == $contrail::deployment_node {
  # Fab scripts are not staring local rabbitmq
  service {'supervisor-support-service':
    ensure => running
  } ->
  class {'contrail::provision':
    node_role => $::contrail::node_role,
  }
}
