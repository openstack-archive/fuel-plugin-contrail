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


def make_allow_all_policy_entry():
    address = types.AddressType(virtual_network='any')
    port = types.PortType(start_port=-1, end_port=-1)
    action = types.ActionListType(simple_action='pass')
    rule = types.PolicyRuleType(
        protocol='any',
        direction='<>',
        src_addresses=[address],
        src_ports=[port],
        dst_addresses=[address],
        dst_ports=[port],
        action_list=action)
    return types.PolicyEntriesType(policy_rule=[rule])


allow_all_policy_entry = make_allow_all_policy_entry()
