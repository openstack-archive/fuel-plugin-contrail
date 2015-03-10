include contrail
if $contrail::node_name =~ /^#${contrail::contrail_node_basename}.\d+$/ {
  class { 'contrail::neutron':
    revision => $contrail::neutron_plugin_revision,
  } ->
  class { 'contrail::config':
    node_role => $contrail::node_role,
    node_name => $contrail::node_name,
  } ~>
  class { 'contrail::service':
    node_role => $contrail::node_role,
  }
}
