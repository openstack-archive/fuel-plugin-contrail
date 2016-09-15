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


require 'hiera'

Facter.add("mac_from_vrouter") do
  setcode do
    output=`vif --get 0`
    hiera = Hiera.new(:config => '/etc/hiera.yaml')
    network_scheme = hiera.lookup('network_scheme', {}, {}, nil, :hash)

    phys_dev = vlan = ''
    network_scheme['transformations'].each do |trans|
      if trans['bridge'] == network_scheme['roles']['neutron/mesh']
        phys_dev, vlan = trans['name'].split('.')
        break
      end
    end

    mac = `cat /sys/class/net/#{phys_dev}/address`.chomp
    if $?.success?
       output.split('vif').each do |iface|
         if iface.start_with?( '0/0')
           mac = iface.split[8][7..-1]
         end
       end
     end
     mac
   end
end

