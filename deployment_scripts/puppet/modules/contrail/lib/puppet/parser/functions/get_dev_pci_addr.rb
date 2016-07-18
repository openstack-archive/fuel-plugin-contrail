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
newfunction(:get_dev_pci_addr, :type => :rvalue, :doc => <<-EOS
      Returns interface's PCI address, else returns "0000:00:00.0"
      Arguments: interface name, network_scheme
    EOS
  ) do |args|
      # Get the real interface name if argument is '<ifname>.<vlanid>'
      if_name = args[0].split('.').first
      network_scheme = args[1]

      raise ArgumentError, 'No interface name is provided!' unless if_name and if_name.length > 0
      raise ArgumentError, 'network_scheme should be a hash!' unless network_scheme.is_a? Hash
      raise ArgumentError, 'There is no "interfaces" section in the network_scheme!' unless network_scheme.key? 'interfaces'

      if_yml = network_scheme['interfaces'][if_name]

      if if_yml and if_yml['vendor_specific']
        if_yml['vendor_specific']['bus_info']
      else
        '0000:00:00.0'
      end
    end
end
