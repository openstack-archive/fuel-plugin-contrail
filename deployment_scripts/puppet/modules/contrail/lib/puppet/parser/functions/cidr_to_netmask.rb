require 'ipaddr'

module Puppet::Parser::Functions
  newfunction(:cidr_to_netmask, :type => :rvalue, :doc => <<-EOS
Convert "CIDR prefix" notation (i.e. /24) to long form (i.e. 255.255.255.0)
EOS
  ) do |args|

    netmask = IPAddr.new("255.255.255.255").mask(args[0]).to_s
    return netmask

  end
end



