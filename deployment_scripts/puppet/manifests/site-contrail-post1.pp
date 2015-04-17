include contrail
Exec { path => '/bin:/sbin:/usr/bin:/usr/sbin', refresh => 'echo NOOP_ON_REFRESH', timeout => 1800}
if $contrail::node_name == $contrail::deployment_node {

  class { 'contrail::testbed': }
  ->
  class { 'contrail::setup':
    node_name => $contrail::node_name,
  }
}
