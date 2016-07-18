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
      get_private_ifname('br-mesh', $network_scheme)
    EOS
  ) do |args|
   br_name = args[0]
   network_scheme = args[1]

   raise ArgumentError, 'No bridge name is provided!' unless br_name and br_name.length > 0
   raise ArgumentError, 'network_scheme should be a hash!' unless network_scheme.is_a? Hash
   raise ArgumentError, 'There is no "transformations" section in the network_scheme!' unless network_scheme.key? 'transformations'

   if_name = nil
   network_scheme['transformations'].each do |entry|
     if_name = entry['name'] if entry['bridge'] == br_name
   end

  if_name
  end
end

