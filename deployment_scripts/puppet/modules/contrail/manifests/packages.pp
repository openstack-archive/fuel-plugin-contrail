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

  include apt

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


  if ($install) {
    if ($responsefile) {
      file { "/var/cache/debconf/${responsefile}" :
        ensure => file,
        source => "puppet:///modules/contrail/${responsefile}",
        before => Package[$install],
      }
       Package {
        responsefile => "/var/cache/debconf/${responsefile}",
      }
    }
    package { $install:
      ensure     => present,
      require    => Apt::Pin['ubuntu'],
    }
  }

  if ($remove) {
    package { $remove:
      ensure     => absent,
      require    => Apt::Pin['ubuntu'],
    }
  }

  if ($pip_install) {
    exec_pip { $pip_install:
      path => '/opt/contrail/python_packages'
    }
  }

}
