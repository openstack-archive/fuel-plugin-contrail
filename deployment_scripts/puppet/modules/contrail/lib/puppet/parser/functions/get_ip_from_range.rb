require 'ipaddr'

module Puppet::Parser::Functions
  newfunction(:get_ip_from_range, :type => :rvalue, :doc => <<-EOS
Returns ip address from range ARG1 to ARG2 with offset of ARG4.
Netmask in short form (i.e. "24") is passed as ARG3.
EOS
  ) do |args|

    new_ip = IPAddr.new(args[0])
    ip_end = IPAddr.new(args[1])
    subnet = IPAddr.new(args[0].to_s+"/"+args[2].to_s)
    offset = args[3].to_i

    offset.times do
        new_ip = new_ip.succ
    end

    if not subnet.include?(new_ip) then
      raise Puppet::ParseError, "IP " + new_ip.to_s + " is out of subnet " + subnet.to_s
    end

    if new_ip > ip_end  then
      raise Puppet::ParseError, "IP " + new_ip.to_s + " is out of allowed ip range. " + ip_end.to_s + " is the max"
    end

    return new_ip

  end
end

