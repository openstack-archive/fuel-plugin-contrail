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
      get_sriov_devices('phys_dev')
    EOS
  ) do |args|

    interface = args[0].sub(/\..*/, '')
    interfaces = Array.new()
    sriov_hash = Hash.new

    network_scheme = function_hiera_hash(['network_scheme', {}])
    network_scheme['transformations'].each do |entry|
      if entry['name'] == interface and entry.has_key?('bond_properties') and entry['action'] == "add-bond"
        interfaces.push(*entry['interfaces'])
      elsif entry['action'] == 'add-port' and entry['name'] == args[0]
        interfaces << interface
      end
    end

    interfaces.each do |interface|
      interface_path = "/sys/class/net/" + interface
      if (File.exists?(interface_path + "/device/sriov_totalvfs"))
        sriov_hash[interface] = Hash.new
        sriov_hash[interface]["totalvfs"] = IO.read(interface_path + "/device/sriov_totalvfs").to_i
        sriov_hash[interface]["numvfs"] = IO.read(interface_path + "/device/sriov_numvfs").to_i
        function_add_data_to_yaml(["/etc/hiera/plugins/contrail.yaml", "sriov_hash", sriov_hash])
      elsif function_hiera_hash(['sriov_hash', {}]).has_key?(interface)
        sriov_hiera = function_hiera_hash(['sriov_hash', {}])
        sriov_hash[interface] = Hash.new
        sriov_hash[interface]["totalvfs"] = sriov_hiera["totalvfs"]
        sriov_hash[interface]["numvfs"] = sriov_hiera["numvfs"]
      end
    end

    return sriov_hash
  end
end
