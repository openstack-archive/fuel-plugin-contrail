class contrail::package (
  $install,
  $remove = undef,
  $pip_install = undef,
  ) {

  if ($install) {

    if $operatingsystem == 'Ubuntu' {
      file { '/etc/apt/preferences.d/contrail-pin-100':
        ensure => file,
        source => 'puppet:///modules/contrail/contrail-pin-100',
        before => Package[$install],
      }
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
