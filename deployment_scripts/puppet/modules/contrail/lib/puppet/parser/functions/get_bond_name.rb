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

module L23network
module Puppet::Parser::Functions
  newfunction(:get_bond_name, :type => :rvalue, :doc => <<-EOS
    Returns bond name, if overrides are not applied
    1) Get network_scheme including overrides
    2) Check if bond is present in scheme
    3) If yes, return raw bond name, otherwise return undef
    example:
      get_bond_name($network_scheme, $contrail::phys_dev, $contrail::compute_dpdk_on_vf)
    used in dpdk-on-vf to determine if bond needs to be created
    EOS
  ) do |argv|
    cfg_hash, interface, dpdk_enabled = argv
    interface_real = interface.split('.').first

    rv = nil

    # this part is a copy from prepare_network_config.rb
    ns = L23network.sanitize_bool_in_hash(L23network.sanitize_keys_in_hash(cfg_hash))
    ns = L23network.override_transformations(ns)
    ns = L23network.remove_empty_members(ns)

    ns[:transformations].each do |t|
      if t[:action] == 'add-bond' and t[:name] == interface_real and dpdk_enabled
         rv = interface_real
      end
    end

    return rv
  end
end
end
