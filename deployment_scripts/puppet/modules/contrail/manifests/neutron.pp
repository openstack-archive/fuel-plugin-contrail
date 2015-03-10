class contrail::neutron ( $revision ) {
  file { '/usr/share/pyshared/neutron_plugin_contrail/plugins/opencontrail':
    ensure  => directory,
    source  => "puppet:///contrail/contrail-neutron-plugin-${revision}",
    recurse => true,
  }
}