begin
  require 'puppetx/l23_network_scheme'
rescue LoadError
  require '/etc/puppet/modules/l23network/lib/puppetx/l23_network_scheme'
end

Puppet::Parser::Functions::newfunction(:get_physdev_mtu, :type => :rvalue, :arity => 1, :doc => <<-EOS
    Returns MTU of a physical interface, including cases where it's a bond
    EOS
  ) do |argv|
  physdev = argv[0]

  cfg = L23network::Scheme.get_config(lookupvar('l3_fqdn_hostname'))
  transformations = cfg[:transformations]
  interfaces = cfg[:interfaces]

  transformations.each do |transform|
    if transform[:name] == physdev
      mtu = transform[:mtu]
      return mtu if mtu
    end
  end

  if interfaces[physdev.to_sym]
    mtu = interfaces[physdev.to_sym][:mtu]
    return mtu if mtu
  end
end
