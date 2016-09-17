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

require 'json'

module Puppet::Parser::Functions
  newfunction(:generate_passthrough_whitelist, :type => :rvalue, :doc => <<-EOS
    Returns pci_passthrough_whitelist for nova config
    EOS
  ) do |args|

    physnet = args[0]
    dpdk_on_vf = args[1]
    sriov_hash = function_get_sriov_devices([])
    network_scheme = function_hiera_hash(['network_scheme', {}])

    list = []
    if function_get_nic_passthrough_whitelist(['sriov'])
      list += function_get_nic_passthrough_whitelist(['sriov'])
    end

    if dpdk_on_vf
      hiera_data_key = "priv_int_vfn_wl"
      priv_int = args[2].sub(/\..*/, '')
      dpdk_vf_number = args[3]
      if (File.exists?("/sys/class/net/#{priv_int}"))
        vfn = Dir.glob "/sys/class/net/#{priv_int}/device/virtfn*"
        vfn_wl = vfn.map { |f|
           if not f.end_with? "virtfn#{dpdk_vf_number}"
             pci_address = File.readlink(f).split("/")[1]
             Hash["address" => pci_address, "physical_network" => physnet]
           end
        }
        list += vfn_wl
        function_add_data_to_yaml(["/etc/hiera/plugins/contrail.yaml", hiera_data_key, vfn_wl])
      elsif not function_hiera_array([hiera_data_key, []]).empty?
        vfn_wl = function_hiera_array([hiera_data_key, []])
        list += vfn_wl
      end
    end

    return list.to_json
  end
end
