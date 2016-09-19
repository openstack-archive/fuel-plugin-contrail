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

module Puppet::Parser::Functions
  newfunction(:get_vf_data, :type => :rvalue, :doc => <<-EOS
    Returns interface name, pci address, mac address related to specific virtual function
    example:
      get_vf_data(dev_name, vf_number)
    EOS
  ) do |args|

    dev_name = args[0].sub(/\..*/, '')
    vf_number = args[1]
    vf_sys = "/sys/class/net/#{dev_name}/device/virtfn#{vf_number}"
    vf_data = Hash.new

    if (File.exists?("/sys/class/net/#{dev_name}/device/virtfn#{vf_number}/net"))
        hiera_data_key = "dpdk_vf_" + vf_number + "_data"
        vf_dev_name = Dir.entries("#{vf_sys}/net/")[2]
        vf_pci_addr = File.readlink(vf_sys).split("/")[1]
        vf_mac_addr = File.open("#{vf_sys}/net/#{vf_dev_name}/address", "rb") { |f| f.read.strip }
        vf_data = {"vf_dev_name" => vf_dev_name, "vf_pci_addr" => vf_pci_addr, "vf_mac_addr" => vf_mac_addr}
        function_add_data_to_yaml(["/etc/hiera/plugins/contrail.yaml", hiera_data_key, vf_data])
    elsif not function_hiera_hash([hiera_data_key, {}]).empty?
      vf_data = function_hiera_hash([hiera_data_key, {}])
    end

    return vf_data
  end
end
