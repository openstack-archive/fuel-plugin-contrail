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
      #NOTE: Contrail requires newer python-thrift and nodejs from its repo
      yumrepo {'mos': priority => 1, exclude => 'python-thrift,nodejs'}
      package {'yum-plugin-priorities': ensure => present }
    }
    Ubuntu: {
      file { "/etc/apt/preferences.d/contrail-${plugin_version}.pref":
        ensure => absent,
      }
      # override packages pins to install tzdata, perl from ubuntu repo instead of
      # contrail repo, version of packages in ubuntu repo is higher, so we dont want
      # to downgrade.
      apt::pin { 'tzdata-java':
       explanation => 'Temporary fix to install tzdata from ubuntu repos',
       priority  => 1300,
       packages  => 'tzdata-java',
       release   => 'trusty',
      }
      apt::pin { 'libperl5.18':
       explanation => 'Temporary fix for contrail analytics',
       priority  => 1300,
       packages  => 'libperl5.18',
       release   => 'trusty',
      }
    }
    default: {}
  }

  install_ssh_keys {'vmware_root_ssh_key':
    ensure           => present,
    user             => 'root',
    private_key_name => 'id_rsa_vmware',
    public_key_name  => 'id_rsa_vmware.pub',
    private_key_path => '/var/lib/astute/vmware/vmware',
    public_key_path  => '/var/lib/astute/vmware/vmware.pub',
  }
}
