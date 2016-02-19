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
​
module Puppet::Parser::Functions
newfunction(:get_dev_pci_addr, :type => :rvalue, :doc => <<-EOS
      Returns interface's PCI address, else returns "0000:00:00.0"
    EOS
  ) do |args|
      # Get the real interface name if argument is '<ifname>.<vlanid>' 
      ifname = args[0].split('.').first
      yml = YAML.load(File.open("/etc/astute.yaml"))
      ifyml = yml['network_scheme']['interfaces'][ifname]

      if ifyml and ifyml['vendor_specific']
        return ifyml['vendor_specific']['bus_info']
      else
        return '0000:00:00.0'
      end
    end
end