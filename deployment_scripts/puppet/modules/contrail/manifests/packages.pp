# requires
#   puppetlabs-apt
#   puppetlabs-stdlib
class contrail::packages (
  $install,
  $remove = undef,
  $responsefile = undef,
  $pip_install = undef,
  ) {

  define exec_pip ( $path ){
    exec { "Install-pip-package-${name}":
      path     => '/usr/local/bin/:/usr/bin:/bin',
      command  => "pip install --upgrade --no-deps --index-url='' ${path}/${name}.tar.gz",
    }
  }

  if ($install) {
    if ($responsefile) {
      file { "/var/cache/debconf/${responsefile}":
        ensure => file,
        source => "puppet:///modules/contrail/${responsefile}",
        before => Package[$install],
      }
      Package {
        responsefile => "/var/cache/debconf/${responsefile}",
      }
    }
    file { '/etc/apt/preferences.d/contrail-pin-100':
      ensure => file,
      source => 'puppet:///modules/contrail/contrail-pin-100',
      before => Package[$install],
    }
    package { $install:
      ensure  => present,
    }
    if ($pip_install) {
      exec_pip { $pip_install:
        path    => '/opt/contrail/python_packages',
        require => Package[$install],
      }
    }
  }

  if ($remove) {
    package { $remove:
      ensure  => absent,
    }
  }

}
