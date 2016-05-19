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
    sriov_hash = function_get_sriov_devices([])

    list = sriov_hash.map { |dev, _|
      #pci_address = `ethtool -i #{dev} | awk '/bus-info/ {print $2}'`.strip
      pci_address = function_get_dev_pci_addr([dev])
      Hash["address" => pci_address, "physical_network" => physnet]
    }.to_json

    return list
  end
end
