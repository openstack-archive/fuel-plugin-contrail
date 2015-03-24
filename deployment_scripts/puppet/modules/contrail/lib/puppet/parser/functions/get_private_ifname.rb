require 'ipaddr'

module Puppet::Parser::Functions
newfunction(:get_private_ifname, :type => :rvalue, :doc => <<-EOS
    Returns interface selected as "Private network" in web UI
    EOS
  ) do |args|
     ifname = String.new
     cfg = L23network::Scheme.get_config(lookupvar('l3_fqdn_hostname'))
     cfg[:transformations].each do |entry|

     if entry[:action] == "add-port" and entry[:bridge] == "br-aux"
       ifname = entry[:name]
     end

   end
        return ifname.to_s
    end
end

