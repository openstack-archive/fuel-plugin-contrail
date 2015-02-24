# requires
#   puppetlabs-apt
#   puppetlabs-stdlib
class contrail::packages (
  $master_ip = hiera('master_ip'),
  $master_port = '8080',
  $plugin_version = $contrail::settings['metadata']['plugin_version'],
  $install = undef,
  $remove = undef,
  $responsefile = undef,
  ) {

  class { 'apt': disable_keys => true }

  apt::source { 'contrail-from-fuel-master':
    location     => "http://${master_ip}:${master_port}/contrail-${plugin_version}/repositories/ubuntu/",
    release      => '',
    repos        => '/',
    include_src  => false,
    require      => Apt::Pin['ubuntu'],
  }

  apt::pin { 'ubuntu':
    order        => 10,
    priority     => 100,
    label        => 'Ubuntu',
    packages     => '*',
  }

  if ($responsefile) {
    file { "/var/cache/debconf/${responsefile}" :
      ensure => file,
      source => "puppet:///modules/contrail/${responsefile}",
      before => Package[$install],
    }
  }

  if ($install) {
    package { $install:
      ensure     => present,
      require    => Apt::Source['contrail-from-fuel-master'],
    }
  }

  if ($remove) {
    package { $remove:
      ensure     => absent,
      require    => Apt::Source['contrail-from-fuel-master'],
    }
  }

}
   