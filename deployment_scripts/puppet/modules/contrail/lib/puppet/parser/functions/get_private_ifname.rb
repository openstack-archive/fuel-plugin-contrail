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

require 'ipaddr'

module Puppet::Parser::Functions
newfunction(:get_private_ifname, :type => :rvalue, :doc => <<-EOS
    Returns interface selected as "Private network" in web UI
    EOS
  ) do |args|
     ifname = String.new
     cfg = L23network::Scheme.get_config(lookupvar('l3_fqdn_hostname'))
     cfg[:transformations].each do |entry|

     if entry[:action] == "add-port" and (entry[:bridge] == "br-aux" or entry[:bridge] == "br-mesh")
       ifname = entry[:name]
     end

   end
        return ifname.to_s
    end
end

