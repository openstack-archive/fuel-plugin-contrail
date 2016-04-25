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

module Puppet::Parser::Functions
newfunction(:fetch_esxi_data, :type => :rvalue, :doc => <<-EOS
    Return esxi data regarding to contrailVM
    EOS
  ) do |args|
    hiera = function_hiera(["contrail"])
    host = args[0]
    user_fab = YAML.load hiera["contrail_vcenter_esxi_for_fabric"]
    user_fab.each { |k, v|
      if v["contrail_vm"]["host"] == host then
        return v
      end
    }
    end
end
