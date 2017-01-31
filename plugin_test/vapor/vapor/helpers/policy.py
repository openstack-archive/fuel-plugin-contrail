# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import pycontrail.types as types


def make_policy_entry(protocol, src_ports_range, dst_ports_range):
    address = types.AddressType(virtual_network='any')
    src_port = types.PortType(
        start_port=src_ports_range[0], end_port=src_ports_range[1])
    dst_port = types.PortType(
        start_port=dst_ports_range[0], end_port=dst_ports_range[1])
    action = types.ActionListType(simple_action='pass')
    rule = types.PolicyRuleType(
        protocol=protocol,
        direction='<>',
        src_addresses=[address],
        src_ports=[src_port],
        dst_addresses=[address],
        dst_ports=[dst_port],
        action_list=action)
    return types.PolicyEntriesType(policy_rule=[rule])


allow_all_policy_entry = make_policy_entry(
    protocol='any', src_ports_range=(-1, -1), dst_ports_range=(-1, -1))
