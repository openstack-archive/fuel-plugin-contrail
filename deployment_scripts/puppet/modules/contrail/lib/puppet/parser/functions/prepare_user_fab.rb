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
require 'yaml'
require 'json'

module Puppet::Parser::Functions
newfunction(:prepare_user_fab, :type => :rvalue, :doc => <<-EOS
    Prepare user data for putting in testbed.py
    EOS
  ) do |args|
    hiera = function_hiera(["contrail"])
    default_fab = args[0]
    user_fab = YAML.load hiera["contrail_vcenter_esxi_for_fabric"]
    full_fab = user_fab
    full_fab.each { |k, v|
      full_fab[k]["vcenter_server"] = default_fab["vcenter_server"]
      full_fab[k]["contrail_vm"]["mode"] = default_fab["mode"]
      full_fab[k]["contrail_vm"]["vmdk"] = default_fab["vmdk"]
    }
    pretty_fab = JSON.pretty_generate full_fab
    return pretty_fab
    end
end

