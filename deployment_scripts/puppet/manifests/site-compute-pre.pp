# Remove automatically installed plugin's repo.
# Some packages conflicts with default repo on openstack-controller nodes
file {"remove-plugin-aptsource":
  # TODO!
  #path => "/etc/apt/sources.list.d/contrail-{plugin_version}.list",
  path => "/etc/apt/sources.list.d/contrail-1.0.0.list",
  ensure => absent,
}
