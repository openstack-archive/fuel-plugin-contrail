
▽
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

module Puppet::Parser::Functions
  newfunction(:list_bond_vf_slaves, :type => :rvalue, :doc => <<-EOS
    #FIXME
    Returns pci_passthrough_whitelist for nova config
    EOS
  ) do | args |

  sriov_hash = function_get_sriov_devices(['bond0.436'])

  b = sriov_hash.map { |k, v| 'dpdk-vf-' + k }
  c = b.join(' ')

  return  c
  end
end
