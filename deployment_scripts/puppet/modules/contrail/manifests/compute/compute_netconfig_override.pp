class contrail::compute::compute_netconfig_override {

  if roles_include('dpdk') {
    # Override network_scheme to skip interfaces used by the vrouter
    $settings = hiera_hash('contrail', {})
    $global_dpdk_enabled  = $settings['contrail_global_dpdk']
    $compute_dpdk_enabled = $global_dpdk_enabled and 'dpdk' in hiera_array('roles')
    $network_scheme = hiera_hash('network_scheme')

    prepare_network_config($network_scheme)
    $phys_dev = get_private_ifname($network_scheme['roles']['neutron/mesh'])
    $override_ns = vrouter_override_network_scheme($network_scheme, $phys_dev, $compute_dpdk_enabled)

    file { '/etc/hiera/plugins/contrail-vrouter-override_ns.yaml':
      ensure  => file,
      content => inline_template('<%= YAML.dump @override_ns %>'),
      replace => false,
    }
    file_line {'contrail-vrouter-override_ns':
      path  => '/etc/hiera.yaml',
      line  => '    - plugins/contrail-vrouter-override_ns',
      after => '  !ruby/sym hierarchy:',
    }
  }

}
