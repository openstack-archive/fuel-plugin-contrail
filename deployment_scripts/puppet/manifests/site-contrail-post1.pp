include contrail
if $contrail::node_name == $contrail::deployment_node {

  class { 'contrail::testbed': }
  ->
  class { 'contrail::setup':
    node_name => $contrail::node_name,
  }
}
