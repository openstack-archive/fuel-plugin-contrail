require 'yaml'

Puppet::Parser::Functions::newfunction( :vrouter_override_network_scheme,
                                        :type => :rvalue, :doc => <<-EOS
    Override network_scheme to skip interfaces used by DPDK vrouter
    1. Get real nic name
    2. Check if interface is a bond
    3. Override bond creation if it is
    4. Override add-port to br-mesh
    5. Override add-br for br-mesh
    6. Override endpoint for br-mesh
    EOS
  ) do |argv|
    override       = {'transformations' => [],
                      'endpoints' => {},
                      'roles' => {},
                      'interfaces' => {}}
    orig_ns        = argv[0]
    interface      = argv[1]
    dpdk_enabled   = argv[2]
    interface_real = interface.split('.').first
    private_bridge = function_get_network_role_property(['neutron/mesh', 'interface'])

    # Overriding transformations
    orig_ns['transformations'].each do |tr|
      if tr['action'] == 'add-bond' and tr['name'] == interface_real and dpdk_enabled
        override['transformations'] << {'action'          => 'override',
                                        'override'        => interface_real,
                                        'override-action' => 'noop'}
      elsif tr['action'] == 'add-port' and tr['name'] == interface
        override['transformations'] << {'action'          => 'override',
                                        'override'        => interface,
                                        'override-action' => 'noop'}
      elsif tr['action'] == 'add-br' and tr['name'] == private_bridge
        override['transformations'] << {'action'          => 'override',
                                        'override'        => private_bridge,
                                        'override-action' => 'noop'}
      end
    end

    # Overriding 'br-mesh' endpoint
    orig_ns['endpoints'].each do |ep_name, ep_data|
      if ep_name == private_bridge
        override['endpoints'][private_bridge] = ''
        override['endpoints']['vhost0'] = orig_ns['endpoints'][private_bridge]
      end
    end

    # Overriding network roles
    orig_ns['roles'].each do |role, ep|
      override['roles'][role] = 'vhost0' if ep == private_bridge
    end

    # Overriding interfaces
    override['interfaces']['vhost0'] = ''

    {'network_scheme' => override}
end
# vim: set ts=2 sw=2 et :