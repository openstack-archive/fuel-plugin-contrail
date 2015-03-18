class contrail::neutron {
  file { '/usr/share/pyshared/neutron_plugin_contrail/plugins/opencontrail':
    ensure  => directory,
    source  => 'puppet:///modules/contrail/opencontrail',
    recurse => true,
  }
}
