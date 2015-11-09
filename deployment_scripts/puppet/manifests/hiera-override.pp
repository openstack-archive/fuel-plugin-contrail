notice('MODULAR: contrail/hiera-override.pp')

$hiera_dir = '/etc/hiera/override'
$plugin_name = 'contrail'
$plugin_yaml = "${plugin_name}.yaml"

$contrail_plugin = hiera('contrail', undef)

if ($contrail_plugin) {
  $neutron_config  = hiera_hash('quantum_settings')
  $nets            = $neutron_config['predefined_networks']


  file {'/etc/hiera/override':
    ensure  => directory,
  }

  file { "${hiera_dir}/${plugin_yaml}":
    ensure  => file,
    content => template('contrail/plugins.yaml.erb'),
    require => File['/etc/hiera/override']
  }

  package {'ruby-deep-merge':
    ensure  => 'installed',
  }

  file_line {"${plugin_name}_hiera_override":
    path  => '/etc/hiera.yaml',
    line  => "  - override/${plugin_name}",
    after => '  - override/module/%{calling_module}',
  }

}
