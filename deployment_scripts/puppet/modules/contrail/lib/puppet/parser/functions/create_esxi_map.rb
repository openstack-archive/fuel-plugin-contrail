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
newfunction(:create_esxi_map, :type => :rvalue, :doc => <<-EOS
    Prepare user data for putting in testbed.py
    EOS
  ) do |args|

    vcenter_hash = function_hiera(['vcenter'])
    compute_vmware_clusters = vcenter_hash['computes'][0]['vc_cluster'].split(',')

    contrail_hash = function_hiera(['contrail'])
    esxi_hash = JSON.parse contrail_hash['contrail_vcenter_esxi_for_fabric']
    map_elements = Array.new

    esxi_hash.each do |esxi_entry|
      if compute_vmware_clusters.include?(esxi_entry['cluster'])
        contrail_vm_ip = esxi_entry['contrail_vm']['host'].spli['@'][1]
        map_elements << [esxi_entry[ip], contrail_vm_ip].join(':')
      end
    end
    return map_elements
  end
end