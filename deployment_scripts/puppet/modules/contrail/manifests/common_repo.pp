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
      $repo_setup_hash              = hiera_hash('repo_setup', {})
      $repos                        = pick($repo_setup_hash['repos'], [])
      $pins                         = generate_apt_pins($repos)
      $ubuntu_pins                  = pick($pins['ubuntu'], {})
      if ! empty($ubuntu_pins) {
        #override packages pins to be intalled from ubuntu repo
        $ubuntu_pins['packages']    = ['tzdata', 'libperl5.18', 'tzdata-java', 'openjdk-7-jre-headless']
        create_resources(apt::pin, {'contrail-pin-exclude' => $ubuntu_pins})
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
