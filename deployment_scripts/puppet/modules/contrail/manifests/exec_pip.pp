# A helper to run pip
define contrail::exec_pip ( $path ){
  exec { "Install-pip-package-${name}":
    path    => '/usr/local/bin/:/usr/bin:/bin',
    command => "pip install --upgrade --no-deps --index-url='' ${path}/${name}.tar.gz",
  }
}