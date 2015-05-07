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
  newfunction(:get_first_ip, :type => :rvalue, :doc => <<-EOS
Returns first ip in subnet. ARG1 - subnet in CIDR notation (i.e. 192.168.1.0/24)
EOS
  ) do |args|
    cidr = IPAddr.new(args[0])
    return cidr.succ.to_s
  end
end


