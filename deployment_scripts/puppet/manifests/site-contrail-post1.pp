if hiera('user_node_name') =~ /^contrail-.\d*$/ {
include contrail

#class { 'contrail::testbed': }

class { 'contrail::setup':
  node_name => $contrail::node_name,
}

}