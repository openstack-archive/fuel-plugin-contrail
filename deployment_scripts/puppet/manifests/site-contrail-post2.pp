include contrail
if $contrail::node_name =~ /^contrail.\d+$/ {
  class { 'contrail::config':
    node_role => $contrail::node_role,
  } ~>
  class { 'contrail::service':
    node_role => $contrail::node_role,
  }
}
