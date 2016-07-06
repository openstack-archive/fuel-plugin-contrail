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

class contrail::utils {

  sysctl::value {
    'net.ipv4.conf.all.rp_filter':  value => '2';
    'net.ipv4.conf.default.rp_filter':  value => '2';
  }

  case $operatingsystem {
    Ubuntu: {
      file { '/etc/apt/preferences.d/contrail-pin-100':
        ensure => file,
        source => 'puppet:///modules/contrail/contrail-pin-100',
      } ->
      exec { 'reinstall-tzdata':
        path    => '/bin:/sbin:/usr/bin:/usr/sbin',
        command => '/usr/bin/apt-get install -y --force-yes tzdata',
        before  => Class['contrail::package'],
      }
      $pkgs = ['python-crypto','python-netaddr','python-paramiko',
        'ifenslave-2.6','patch','openjdk-7-jre-headless',
        'python-contrail','contrail-setup','contrail-utils','contrail-nodemgr','supervisor']

      #Fix for certifi CA blocking self signed certificates
      if $contrail::public_ssl {
        file{'/usr/lib/python2.7/dist-packages/certifi/cacert.pem':
          ensure  => 'link',
          target  => '/etc/ssl/certs/ca-certificates.crt',
          require => Package['python-contrail']
        }
      }
    }

    CentOS: {
      $pkgs     = ['python-netaddr','python-paramiko','patch',
        'java-1.7.0-openjdk','contrail-fabric-utils','contrail-setup']
      $pip_pkgs = ['Fabric-1.7.5']
    }

    default: {}
  }

  class { 'contrail::package':
    install     => $pkgs,
    pip_install => $pip_pkgs,
  } ->

  file { '/etc/contrail/vnc_api_lib.ini':
    content => template('contrail/vnc_api_lib.ini.erb')
  }

}
