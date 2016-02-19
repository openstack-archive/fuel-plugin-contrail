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
newfunction(:get_mac_from_vrouter, :type => :rvalue, :doc => <<-EOS
      Returns mac address of interface used by DPDK vrouter
    EOS
  ) do |args|
      mac = "00:00:00:00:00:00"

      begin
        output=`vif --list`
        result=$?.success?
        if result
          for int in output.split('vif')
            if int.start_with?( '0/0')
              mac = int.split[8][7..-1]
            end
          end
        end
      rescue Exception
        warning 'Could not retrieve correct mac address from vrouter. Probably vrouter is running incorrectly.'
      end
      return mac
    end
end

