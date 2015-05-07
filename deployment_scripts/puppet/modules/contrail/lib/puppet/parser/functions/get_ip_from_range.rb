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
  newfunction(:get_ip_from_range, :type => :rvalue, :doc => <<-EOS
Returns ip address from range ARG1 to ARG2 with shift of ARG4.
Netmask in short form (i.e. "24") is passed as ARG3.
ARG5 "first" or "last" sets the direction of address shift in range: first-to-last or last-to-first.

get_ip_from_range("range_start","range_end","cidr_netmask","offset","first|last")
EOS
  ) do |args|

    ip_start = IPAddr.new(args[0].to_s)
    ip_end = IPAddr.new(args[1].to_s)
    subnet = IPAddr.new(args[0].to_s+"/"+args[2].to_s)
    offset = args[3].to_i

    case args[4]
    when "last"
      rv = ip_end
      offset.times do
          rv = rv.prev
      end
    when "first"
      rv = ip_start
      offset.times do
          rv = rv.succ
      end
    else
      raise Puppet::ParseError, "Wrong argument " + args[4].to_s
    end

    if not subnet.include?(rv) then
      raise Puppet::ParseError, "IP " + rv.to_s + " is out of subnet " + subnet.to_s
    end

    if rv > ip_end  then
      raise Puppet::ParseError, "IP " + rv.to_s + " is out of allowed ip range. " + ip_end.to_s + " is the max"
    end

    return rv.to_s

  end
end

