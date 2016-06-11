#    Copyright 2016 Mirantis, Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

Puppet::Parser::Functions::newfunction( :vrouter_override_network_scheme,
                                        :type => :rvalue, :arity => 3, :doc => <<-EOS
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
    orig_ns, interface, dpdk_enabled = argv
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
    override['roles']['contrail/vhost0'] = 'vhost0'

    # Overriding interfaces
    override['interfaces']['vhost0'] = {}

    {'network_scheme' => override}
end
# vim: set ts=2 sw=2 et :
