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

notice('MODULAR: contrail/common-repo.pp')

$settings = hiera('contrail', {})
$plugin_version = regsubst($settings['metadata']['plugin_version'], '..$' , '')

file { "/etc/apt/preferences.d/contrail-${plugin_version}.pref":
  ensure => absent,
}

if roles_include(['primary-controller','controller']) {

  apt::pin { 'patched_neutronclient':
    explanation => 'Horizon tab requires patched client',
    packages    => 'python-neutronclient',
    priority    => '1300',
    label       => 'contrail',
  }

}
