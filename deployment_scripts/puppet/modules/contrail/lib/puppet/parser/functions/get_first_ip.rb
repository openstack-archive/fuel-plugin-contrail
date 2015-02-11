require 'ipaddr'

module Puppet::Parser::Functions
  newfunction(:get_first_ip, :type => :rvalue, :doc => <<-EOS
Returns first ip in subnet. ARG1 - subnet in CIDR notation (i.e. 192.168.1.0/24)
EOS
  ) do |args|
    cidr = IPAddr.new(args[0])
    return cidr.succ
  end
end


