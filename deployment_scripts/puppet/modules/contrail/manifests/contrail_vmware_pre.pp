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

class contrail::contrail_vmware_pre {

  if $contrail::use_vcenter {

    $delete_packages  = ['openvswitch-common', 'openvswitch-datapath-dkms',
      'openvswitch-datapath-lts-saucy-dkms', 'openvswitch-switch', 'nova-network',
      'nova-api']

    $install_packages = ['contrail-install-packages', 'contrail-fabric-utils',
      'contrail-setup', 'contrail-vrouter-dkms', 'contrail-vrouter-common',
      'contrail-nova-vif', 'open-vm-tools', 'iproute2', 'python-pyvmomi', 'python-urllib3']

    class { 'contrail::package':
      install => [$install_packages],
      remove  => [$delete_packages],
    }

    file { 'vrouter_to_esxi_map' :
      ensure  => present,
      owner   => 'root',
      group   => 'root',
      mode    => '0755',
      content => template('contrail/vrouter_to_esxi_map.py.erb'),
      path    => '/usr/local/bin/vrouter_to_esxi_map',
    }

    vcenter_vrouter_map { 'contrail-esxi-vrouter-map.yaml' :
      ensure       => present,
      password     => $contrail::vcenter_server_pass,
      username     => $contrail::vcenter_server_user,
      vcenter_host => $contrail::vcenter_server_ip,
      ips          => $contrail::contrail_vcenter_vm_ips,
      path         => '/etc/hiera/plugins/contrail-esxi-vrouter-map.yaml',
      yaml         => true,
    }

    Class['contrail::package']  -> Vcenter_vrouter_map['contrail-esxi-vrouter-map.yaml']
    File['vrouter_to_esxi_map'] -> Vcenter_vrouter_map['contrail-esxi-vrouter-map.yaml']


  }
}
