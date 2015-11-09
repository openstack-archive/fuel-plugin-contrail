notice('MODULAR: contrail/hiera-override.pp')

$hiera_dir = '/etc/hiera/override'
$plugin_name = 'contrail'
$plugin_yaml = "${plugin_name}.yaml"

$contrail_plugin = hiera('contrail', undef)

if ($contrail_plugin) {
  $neutron_config  = hiera_hash('quantum_settings')
  $nets            = $neutron_config['predefined_networks']


  $calculated_content = inline_template('
quantum_settings: {predefined_networks: false}
<% if @nets -%>
<% require "yaml" -%>
ostf_nets:
<%= YAML.dump(@nets).sub(/--- *$/,"") %>
<% end -%>
  ')

  file {'/etc/hiera/override':
    ensure  => directory,
  }

  file { "${hiera_dir}/${plugin_yaml}":
    ensure  => file,
    content => "${calculated_content}\n",
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
