module Puppet::Parser::Functions
  newfunction(:interface_name_by_mac, :type => :rvalue, :doc => <<-EOS
Find the interface of this node by the mac address or the list of mac addresses.
  EOS
  ) do |*arguments|

    find_top_scope = lambda do |scope|
      unless scope.respond_to? :parent and scope.respond_to? :symtable
        class << scope
          attr_reader :parent
          attr_reader :symtable
        end
      end
      if scope.parent
        find_top_scope.call scope.parent
      else
        scope
      end
    end

    get_symbols = lambda do |scope|
      unless scope.respond_to? :symtable
        class << scope
          attr_reader :symtable
        end
      end
      symtable = scope.symtable
      unless symtable.respond_to? :symbols
        class << symtable
          attr_reader :symbols
        end
      end
      symtable.symbols
    end

    get_interfaces = lambda do |symbols|
      interfaces = {}
      symbols.each do |name, value|
        next unless name =~ /^macaddress_(.*)/
        interfaces[$1] = value
      end
      interfaces
    end

    normalize_mac_address = lambda do |mac_address|
      mac_address = mac_address.downcase
      mac_address.gsub '-', ':'
    end

    mac_address_in_list = lambda do |list_of_mac_addresses, mac_address_to_find|
      list_of_mac_addresses.flatten!
      list_of_mac_addresses.find do |mac_address|
        normalize_mac_address.call(mac_address) == normalize_mac_address.call(mac_address_to_find)
      end
    end

    find_listed_mac_address = lambda do |interfaces, listed_mac_addresses|
      found_interface_names = []
      interfaces.each do |interface, mac_address|
        found_interface_names << interface if mac_address_in_list.call listed_mac_addresses, mac_address
      end
      found_interface_names
    end

    find_listed_mac_address.call (get_interfaces.call get_symbols.call find_top_scope.call self), arguments
  end
end

