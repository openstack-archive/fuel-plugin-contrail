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

include contrail
Exec { path => '/bin:/sbin:/usr/bin:/usr/sbin', refresh => 'echo NOOP_ON_REFRESH', timeout => 1800}

if $contrail::node_name =~ /^contrail.\d+$/ {

  case $operatingsystem
    {
      Ubuntu:
        {
          $pkgs = ['python-crypto','python-netaddr','python-paramiko','ifenslave-2.6','patch',
                  'openjdk-7-jre-headless','contrail-fabric-utils','contrail-setup']
          $pip_pkgs = ['ecdsa-0.10','Fabric-1.7.0']
          }
      CentOS:
        {
          $pkgs = ['python-netaddr','python-paramiko','patch',
                  'java-1.7.0-openjdk','contrail-fabric-utils','contrail-setup']
          $pip_pkgs = ['Fabric-1.7.0']
        }
    }
  class { 'contrail::package':
    install        => $pkgs,
    pip_install    => $pip_pkgs,
  }
}

if $contrail::node_name == $contrail::deployment_node {

  class { 'contrail::testbed':
    require => Class[contrail::package],
  }
  ->
  class { 'contrail::setup':
    node_name => $contrail::node_name,
  }
}
