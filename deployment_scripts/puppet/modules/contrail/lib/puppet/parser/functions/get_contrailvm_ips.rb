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
newfunction(:get_contrailvm_ips, :type => :rvalue, :doc => <<-EOS
    Return list of ContrailVM ips
    EOS
  ) do |args|
     vm_ips = []
     hiera = function_hiera(["contrail"])
     user_fab = YAML.load hiera["contrail_vcenter_esxi_for_fabric"]
     user_fab.each do |_, v|
       if v.key?("contrail_vm")
         vm_ips << v["contrail_vm"]["host"]
       end
     end
    return vm_ips
    end
end
