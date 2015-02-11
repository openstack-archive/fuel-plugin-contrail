require 'ipaddr'

class IPAddr
# New method. Returns the previous ip addr
  def prev
    return self.clone.set(@addr - 1, @family)
  end
end 

module Puppet::Parser::Functions
  newfunction(:get_last_ip, :type => :rvalue, :doc => <<-EOS
Returns last ip in subnet. ARG1 - subnet in CIDR notation (i.e. 192.168.1.0/24)
EOS
  ) do |args|

    cidr = IPAddr.new(args[0])
    prefix=args[0].split('/')[1]
    netmask=IPAddr.new('255.255.255.255').mask(prefix)
    broadcast=cidr.|(netmask.~()) 
    return broadcast.prev    

  end
end


