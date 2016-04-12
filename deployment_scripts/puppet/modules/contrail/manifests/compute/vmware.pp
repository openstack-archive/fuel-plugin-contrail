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

class contrail::compute::vmware {

  file{'/root/.ssh/authorized_keys':
    ensure => present,
    mode   => '0600',
  }

  file_line{'vmware pub authorized keys':
    path => '/root/.ssh/authorized_keys',
    line => file('/var/lib/astute/vmware/vmware.pub')
  }

  $vcenter_compute_pkgs = [
    'nova-compute',
    'nova-compute-kvm',
    'python-novaclient', 'python-bitstring',
    'contrail-utils', 'openjdk-7-jre-headless']:

  package { $vcenter_compute_pkgs:
    ensure => installed,
  }

  $vcenter_plugin_depend_pkgs = [
    'libxml-commons-external-java',
    'libxml-commons-resolver1.1-java',
    'libxerces2-java',
    'libslf4j-java',
    'libnetty-java',
    'libjline-java',
    'libzookeeper-java'
  ]

  $vcenter_plugin_pkgs = [
    'contrail-vcenter-plugin',
    'libcontrail-java-api',
    'libcontrail-vijava',
    'libcontrail-vrouter-java-api',
  ]

  package { $vcenter_plugin_depend_pkgs:
    ensure => installed,
  } ->

  package { $vcenter_plugin_pkgs :
    ensure => installed,
  }

}
