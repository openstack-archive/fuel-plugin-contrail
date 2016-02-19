require 'yaml'
​
module Puppet::Parser::Functions
newfunction(:get_dev_pci_addr, :type => :rvalue, :doc => <<-EOS
      Returns interface's PCI address, else returns "0000:00:00.0"
    EOS
  ) do |args|
      # Get the real interface name if argument is '<ifname>.<vlanid>' 
      ifname = args[0].split('.').first
      yml = YAML.load(File.open("/etc/astute.yaml"))
      ifyml = yml['network_scheme']['interfaces'][ifname]

      if ifyml and ifyml['vendor_specific']
        return ifyml['vendor_specific']['bus_info']
      else
        return '0000:00:00.0'
      end
    end
end