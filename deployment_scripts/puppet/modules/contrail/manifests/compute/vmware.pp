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

  $pkgs = ['contrail-fabric-utils','contrail-setup']
  $pip_pkgs = ['Fabric-1.7.5']

  class { 'contrail::package':
    install     => $pkgs,
    pip_install => $pip_pkgs,
  }

  file_line{'vmware pub authorized keys':
    path => '/root/.ssh/authorized_keys',
    line => file('/var/lib/astute/vmware/vmware.pub')
  }

  #Create a pinning
  $vcenter_compute_pkgs = [
    'nova-compute', 'nova-compute-kvm',
    'python-novaclient', 'python-bitstring',
    'contrail-utils', 'openjdk-7-jre-headless',
    'nova-common']

  exec { 'fix wrong tzdata':
    command => 'apt-get install tzdata -y --force-yes',
    path    => '/bin:/sbin:/usr/bin:/usr/sbin',
    unless  => "apt-cache policy tzdata | grep '*' -A 2 | grep contrail"
  } ->

  apt::pin { 'favor_contrail_packages':
    priority => 1400,
    label    => 'contrail',
    packages => $vcenter_compute_pkgs
  }

  package { $vcenter_compute_pkgs:
    ensure  => installed,
    require => Apt::Pin['favor contrail packages'],
  }

  $vcenter_plugin_depend_pkgs = [
    'libxml-commons-external-java', 'libxml-commons-resolver1.1-java',
    'libxerces2-java', 'libslf4j-java', 'libnetty-java', 'libjline-java',
    'libzookeeper-java']

  $vcenter_plugin_pkgs = [
    'contrail-vcenter-plugin', 'libcontrail-java-api',
    'libcontrail-vijava', 'libcontrail-vrouter-java-api']

  package { $vcenter_plugin_depend_pkgs:
    ensure  => installed,
    require => Apt::Pin['favor contrail packages'],
  } ->

  package { $vcenter_plugin_pkgs :
    ensure  => installed,
    require => Apt::Pin['favor contrail packages'],
  }

}
