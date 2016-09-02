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
  newfunction(:get_node_private_ip, :type => :rvalue, :doc => <<-EOS
    Returns privat ip of node.
    EOS
  ) do |args|
    network_metadata = args[0]
    admin_ip = args[1]
    privat_ip = nil
    network_metadata['nodes'].each do |_, v|
      ips = v['network_roles']
      if ips['admin/pxe'] == admin_ip then
        privat_ip = ips['neutron/mesh']
      end
    end
    return privat_ip
  end
end
