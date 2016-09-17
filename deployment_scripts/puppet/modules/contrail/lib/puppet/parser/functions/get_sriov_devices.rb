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

module Puppet::Parser::Functions
  newfunction(:get_sriov_devices, :type => :rvalue, :doc => <<-EOS
    Returns sriov capable devices
    example:
      get_sriov_devices()
    EOS
  ) do |args|

    dpdk_on_vf = args[0]
    bridge_interfaces = Array.new()
    bond_interfaces = Array.new()

    network_scheme = function_hiera_hash(['network_scheme', {}])
    network_scheme['transformations'].each do |entry|
       if entry.has_key?('bridge') and entry['action'] == "add-port"
         bridge_interfaces.push(entry['name'])
       end
       if entry.has_key?('bond_properties') and entry['action'] == "add-bond"
         bond_interfaces.push(*entry['interfaces'])
       end
    end

    sriov_hash = Hash.new

    if dpdk_on_vf
      hiera_data_key = "priv_int_sriov_data"
      private_interface = args[1].sub(/\..*/, '')
      private_interface_path = "/sys/class/net/" + private_interface
      if (File.exists?(private_interface_path + "/device/sriov_totalvfs"))
        sriov_hash[private_interface] = Hash.new
        sriov_hash[private_interface]["totalvfs"] = IO.read(private_interface_path + "/device/sriov_totalvfs").to_i
        sriov_hash[private_interface]["numvfs"] = IO.read(private_interface_path + "/device/sriov_numvfs").to_i
        function_add_data_to_yaml(["/etc/hiera/plugins/contrail.yaml", hiera_data_key, sriov_hash[private_interface]])
      elsif not function_hiera_hash([hiera_data_key, {}]).empty?
        sriov_hiera = function_hiera_hash([hiera_data_key, {}])
        sriov_hash[private_interface] = Hash.new
        sriov_hash[private_interface]["totalvfs"] = sriov_hiera["totalvfs"]
        sriov_hash[private_interface]["numvfs"] = sriov_hiera["numvfs"]
      end
    end

    return sriov_hash
  end
end
