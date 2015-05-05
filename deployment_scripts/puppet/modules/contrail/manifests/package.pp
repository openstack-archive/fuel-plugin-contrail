class contrail::package (
  $install,
  $remove = undef,
  $pip_install = undef,
  ) {

  # A helper to run pip
  define exec_pip ( $path ){
    exec { "Install-pip-package-${name}":
      path    => '/usr/local/bin/:/usr/bin:/bin',
      command => "pip install --upgrade --no-deps --index-url='' ${path}/${name}.tar.gz",
    }
  }

  if ($install) {

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
