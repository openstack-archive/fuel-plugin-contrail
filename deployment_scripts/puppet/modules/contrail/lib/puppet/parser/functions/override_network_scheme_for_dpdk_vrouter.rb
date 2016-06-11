require 'yaml'

Puppet::Parser::Functions::newfunction( :override_network_scheme_for_dpdk_vrouter,
                                        :type => :rvalue, :doc => <<-EOS
    Override network_scheme to skip interfaces used by DPDK vrouter
    1. Get non-vlan interface name
    2. Check if interface is a bond
    3. Override bond creation if it exists
    4. Override add-port to br-mesh
    5. Override add-br for br-mesh
    6. Override endpoint for br-mesh
    EOS
  ) do |argv|
    override       = {'transformations' => [], 'endpoints' => {}}
    orig_ns        = argv[0]
    interface      = argv[1]
    interface_real = interface.split('.').first
    private_bridge = function_get_network_role_property(['neutron/mesh', 'interface'])

    # Overriding transformations
    orig_ns['transformations'].each do |tr|
      if tr['action'] == 'add-bond' and tr['name'] == interface_real
        override['transformations'] << {'action' => 'override',
                                        'override' => interface_real,
                                        'override-action' => 'noop'}
      elsif tr['action'] == 'add-port' and tr['name'] == interface
        override['transformations'] << {'action' => 'override',
                                        'override' => interface,
                                        'override-action' => 'noop'}
      elsif tr['action'] == 'add-br' and tr['name'] == private_bridge
        override['transformations'] <<  {'action' => 'override',
                                         'override' => private_bridge,
                                         'override-action' => 'noop'}
      end
    end

    # Overriding 'br-mesh' endpoint
    orig_ns['endpoints'].each do |ep_name, ep_data|
      if ep_name == private_bridge
        override['endpoints'][private_bridge] = ''
      end
    end

    return {'network_scheme' => override}
end
# vim: set ts=2 sw=2 et :