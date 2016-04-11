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

class contrail::controller::vmware {

  if $contrail::use_vcenter {

    if $contrail::env == 'dev' {
      file_line { 'change_memsize1':
        path    => '/opt/contrail/utils/fabfile/templates/compute_vmx_template.py',
        line    => 'memsize = "2048"',
        match   => '^memsize',
        require => Class['contrail::package'],
        before  => Exec['fab_prov_esxi'],
      }

      file_line { 'change_memsize2':
        path    => '/opt/contrail/utils/fabfile/templates/compute_vmx_template.py',
        line    => 'sched.mem.min = "2048"',
        match   => '^sched\.mem\.min',
        require => Class['contrail::package'],
        before  => Exec['fab_prov_esxi'],
      }

      #This is temporary solution for development purposes
      file { '/root/.ssh/id_rsa':
        mode   => '0600',
        source => 'puppet:///modules/contrail/vmware_priv',
        before => Exec['fab_prov_esxi'],
      }

      file { '/root/.ssh/id_rsa.pub':
        mode   => '0644',
        source => 'puppet:///modules/contrail/vmware_pub',
        before => Exec['fab_prov_esxi'],
      }

    }

    $pkgs = ['contrail-fabric-utils','contrail-setup']
    $pip_pkgs = ['Fabric-1.7.5']

    class { 'contrail::package':
      install     => $pkgs,
      pip_install => $pip_pkgs,
    }

    exec {'retrive install packages':
      command => "/usr/bin/curl -fLO http://${::contrail::master_ip}:8080/plugins/contrail-3.0/latest-contrail-install-packages.deb",
      creates => '/opt/contrail/contrail-install-packages.deb',
      cwd     => '/opt/contrail',
      before  => Exec['fab_prov_esxi'],
      require => Class['contrail::package'],
    }

    exec {'retrive vmware plugin packages':
      command => "/usr/bin/curl -fLO http://${::contrail::master_ip}:8080/plugins/contrail-3.0/latest-contrail-install-vcenter-plugin.deb",
      creates => '/opt/contrail/contrail-install-vcenter-plugin.deb',
      cwd     => '/opt/contrail',
      before  => Exec['fab_prov_esxi'],
      require => Class['contrail::package'],
    }

    exec {'retrive vmdk':
      command => "/usr/bin/curl -fLO http://${::contrail::master_ip}:8080/plugins/contrail-3.0/ContrailVM-disk1.vmdk",
      creates => '/opt/contrail/ContrailVM-disk1.vmdk',
      cwd     => '/opt/contrail',
      before  => Exec['fab_prov_esxi'],
      require => Class['contrail::package'],
    }

    file { '/opt/contrail/utils/fabfile/testbeds/testbed.py':
      content => template('contrail/vmware_testbed.py.erb'),
      mode    => '0775',
      before  => Exec['fab_prov_esxi'],
      require => Class['contrail::package'],
    }

    exec { 'fab_prov_esxi':
        path    => '/usr/local/bin:/bin:/usr/bin/',
        cwd     => '/opt/contrail/utils',
        command => 'fab prov_esxi && touch /opt/contrail/fab_prov_esxi-DONE',
        creates => '/opt/contrail/fab_prov_esxi-DONE',
    }

  }
}
