#!/usr/bin/env python
#    Copyright 2015 Mirantis, Inc.
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

#    This script is used to get the vcenter settings from FUEL and share them
#    to other roles. By-default FUEL puts these settings only on compute-vmware
#    node. We need them on controller, compute and contrail-vmware nodes.
#    We gather the data from env and convert it to the appropriate format
#    used by the plugin and put as a hiera extension on all nodes.
#
#    Example: $0 <env_id>
#    Example: ./get_vmware_settings.py 5
#
#    By AKirilochkin@mirantis.com

import os
import sys
import yaml
from fuelclient.objects import Environment


env = Environment(sys.argv[1])
attrs_json = env.get_vmware_settings_data()
try:
    attrs_json = attrs_json['editable']['value']['availability_zones'][0]
except:
    print 'Could not parse vmware data from API'

complist = []
for comps in attrs_json['nova_computes']:
    compute = {
        'availability_zone_name' : attrs_json['az_name'],
        'datastore_regex'        : comps['datastore_regex'],
        'service_name'           : comps['service_name'],
        'target_node'            : comps['target_node']['current']['id'],
        'vc_cluster'             : comps['vsphere_cluster'],
        'vc_host'                : attrs_json['vcenter_host'],
        'vc_password'            : attrs_json['vcenter_password'],
        'vc_user'                : attrs_json['vcenter_username'],
    }
    complist.append(compute)

vcenter = {
    'vcenter': {
        'esxi_vlan_interface' : "",
        'computes'            : complist,
    },
}

path = '/var/lib/fuel/contrail/'
try:
    os.makedirs(path)
except OSError:
    if os.path.exists(path):
        pass
    else:
        raise

filepath = '/var/lib/fuel/contrail/{CLUSTER}.yaml'
with open(filepath.format(CLUSTER=sys.argv[1]), 'w') as outfile:
    outfile.write(yaml.safe_dump(vcenter))

