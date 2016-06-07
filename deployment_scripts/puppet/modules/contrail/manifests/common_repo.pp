#    Copyright 2016 Mirantis, Inc.
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

class contrail::common_repo {

  $settings       = hiera_hash('contrail', {})
  $plugin_version = $settings['metadata']['plugin_version']

  case $::operatingsystem {
    CentOS: {
      #NOTE: Contrail requires newer python-thrift and nodejs from it's repo
      yumrepo {'mos': priority => 1, exclude => 'python-thrift,nodejs'}
      package {'yum-plugin-priorities': ensure => present }
    }
    Ubuntu: {
      file { "/etc/apt/preferences.d/contrail-${plugin_version}.pref":
        ensure => absent,
      }
      apt::pin { 'dependency-fix':
        explanation => 'Temporary fix for contrail analytics',
        packages    => 'libperl5.18',
        priority    => 1400,
        version     => '5.18.2-2ubuntu1.1',
      }
    }
    default: {}
  }
}

file_line {'vmware pub authorized keys':
  path   => '/root/.ssh/authorized_keys',
  line => file('/var/lib/astute/vmware/vmware.pub'),
}

