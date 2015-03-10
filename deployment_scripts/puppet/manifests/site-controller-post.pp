include contrail
class { 'contrail::config':
  node_role => $contrail::node_role,
} ~>
class { 'contrail::service':
  node_role => $contrail::node_role,
}
