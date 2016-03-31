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


require 'yaml'

module Puppet::Parser::Functions
  newfunction(:get_sriov_devices, :type => :rvalue, :doc => <<-EOS
    Returns sriov capable devices
    example:
      get_sriov_devices()
    EOS
  ) do |args|

    bridge_interfaces = Array.new()
    bond_interfaces = Array.new()

    if File.exist?('/etc/astute.yaml')
      yml = YAML.load(File.open("/etc/astute.yaml"))
      yml['network_scheme']['transformations'].each do |entry|
         if entry.has_key?('bridge') and entry['action'] == "add-port"
           bridge_interfaces.push(entry['name'])
         end
         if entry.has_key?('bond_properties') and entry['action'] == "add-bond"
           bond_interfaces.push(*entry['interfaces'])
         end
      end
    end

    sriov_hash = Hash.new

    Dir.foreach('/sys/class/net') do |network_interface|
      next if network_interface == '.' or network_interface == '..'
      network_interface_path = "/sys/class/net/" + network_interface
      if (File.exists?(network_interface_path + "/device/sriov_totalvfs") and
          not bridge_interfaces.include?(network_interface) and
          not bond_interfaces.include?(network_interface))
        sriov_hash[network_interface] = Hash.new
        sriov_hash[network_interface]["totalvfs"] = IO.read(network_interface_path + "/device/sriov_totalvfs").to_i
        sriov_hash[network_interface]["numvfs"] = IO.read(network_interface_path + "/device/sriov_numvfs").to_i
      end
    end

    return sriov_hash
  end
end

