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

notice('MODULAR: contrail/contrail-compute-repo.pp')

include contrail

$common_pkg = ['iproute2', 'haproxy', 'libatm1']
$nova_pkg   = ['nova-compute', 'nova-common', 'python-nova', 'python-urllib3']

if $contrail::compute_dpdk_enabled and $contrail::install_contrail_nova {
  $override_pkg = concat($common_pkg, $nova_pkg)
} else {
  $override_pkg = $common_pkg
}

apt::pin { 'contrail-main':
  explanation => 'Set priority for common contrail packages',
  priority    => 200,
  label       => 'contrail',
}

apt::pin { 'contrail-override':
  explanation => 'Set priority for packages that need to override from contrail repository',
  priority    => 1200,
  label       => 'contrail',
  packages    => $override_pkg,
}

