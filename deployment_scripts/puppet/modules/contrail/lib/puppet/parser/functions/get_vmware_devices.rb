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
  newfunction(:get_vmware_devices, :type => :rvalue, :doc => <<-EOS
    Returns device name for internal vmware traffic
    example:
      get_vmware_devices()
    EOS
  ) do |args|

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

    Dir.foreach('/sys/class/net') do |network_interface|
      next if network_interface == '.' or network_interface == '..'
      network_interface_path = "/sys/class/net/" + network_interface
      if (not bridge_interfaces.include?(network_interface) and
        not bond_interfaces.include?(network_interface))
        int_driver = network_interface_path + '/device/driver/module'
        if File.exist?(int_driver)
          path = File.readlink(network_interface_path + '/device/driver/module')
          driver_name = path.split('/')[-1]
          return network_interface
        end
      end
    end
  end
end
