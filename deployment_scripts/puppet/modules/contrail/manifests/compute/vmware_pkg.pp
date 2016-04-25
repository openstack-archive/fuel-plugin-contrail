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

class contrail::compute::vmware_pkg {

Package {
  ensure => installed,
}

#Create a pinning
$vcenter_compute_pkgs = [
  'nova-compute', 'nova-compute-kvm',
  'nova-common', 'nova-compute-libvirt',
  'python-novaclient', 'python-bitstring',
  'tzdata','openjdk-7-jre-headless']

exec { 'fix wrong tzdata':
  command => 'apt-get install tzdata -y --force-yes',
  path    => '/bin:/sbin:/usr/bin:/usr/sbin',
} ->
package { $vcenter_compute_pkgs: }

# Install vCenter-specific contrail packages
package { ['libxml-commons-external-java', 'libxml-commons-resolver1.1-java', 'libxerces2-java',
            'libslf4j-java', 'libnetty-java', 'libjline-java', 'libzookeeper-java']: } ->
package { 'contrail-install-vcenter-plugin': } ->
package { ['libcontrail-java-api','libcontrail-vijava','libcontrail-vrouter-java-api']: } ->
package { 'contrail-vcenter-plugin': }

}
