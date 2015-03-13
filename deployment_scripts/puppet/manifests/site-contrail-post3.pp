include contrail
if $contrail::node_name == $contrail::deployment_node {
  class {'contrail::provision':
    node_role => $contrail::node_role,
  }
}
