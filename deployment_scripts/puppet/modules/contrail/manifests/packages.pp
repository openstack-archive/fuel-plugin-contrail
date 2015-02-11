# requires
#   puppetlabs-apt
#   puppetlabs-stdlib
class contrail::packages (
  $master_ip,
  $master_port = '8080',
  $plugin_version,
  $install,
  $remove = undef,
  $responsefile = undef,
  $pip_install = undef,
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

  define exec_pip ( $path ){
    exec { "Install-pip-package-${name}":
      path     => '/usr/local/bin/:/usr/bin:/bin',
      command  => "pip install --upgrade --no-deps --index-url='' ${path}/${name}.tar.gz",
    }
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
  
  if ($pip_install) {
    exec_pip { $pip_install:
      path => '/opt/contrail/python_packages'
    }
  }

}
   