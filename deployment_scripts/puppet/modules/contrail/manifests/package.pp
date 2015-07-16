#    Copyright 2015 Mirantis, Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

class contrail::package (
  $install,
  $remove = undef,
  $pip_install = undef,
  ) {

  define contrail::package::exec_pip ( $path ){
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
      contrail::package::exec_pip { $pip_install:
        path    => '/opt/contrail/python_packages',
        require => Package[$install],
      }
    }
  }

  if ($remove) {
    package { $remove:
      ensure  => purged,
    }
  }

}
