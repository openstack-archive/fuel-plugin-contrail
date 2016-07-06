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
newfunction(:get_private_ifname, :type => :rvalue, :doc => <<-EOS
    Returns interface selected as "Private network" in web UI
    example:
      get_private_ifname('br-mesh')
    EOS
  ) do |args|
     brname = args[0]
     ifname = String.new
     network_scheme = function_hiera_hash(['network_scheme', {}])

     network_scheme['transformations'].each do |entry|
       if entry['bridge'] == brname
         ifname = entry['name']
       end
    end

    return ifname.to_s
    end
end

