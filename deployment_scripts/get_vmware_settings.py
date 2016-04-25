#!/usr/bin/env python
#
# Example: $0 <env_id>
# Example: ./get_vmware_settings.py 5
#
# By AKirilochkin@mirantis.com

from fuelclient.objects import Environment
import json
import yaml
import sys

try:
    env = Environment(sys.argv[1])
    attrs_json = json.loads(json.dumps(env.get_vmware_settings_data()))
except:
    print 'Could not fetch data for cluster_id: %s' % sys.argv[1]
    sys.exit(1)
try:
    attrs_json = attrs_json['editable']['value']['availability_zones']
except:
    print 'Could not parse vmware data from API'

complist = []
for comps in attrs_json[0]['nova_computes']:
    compute = {
        'availability_zone_name': attrs_json[0]['az_name'].encode('ascii','ignore'),
        'datastore_regex'       : comps['datastore_regex'].encode('ascii','ignore'),
        'service_name'          : comps['service_name'].encode('ascii','ignore'),
        'target_node'           : comps['target_node']['current']['id'].encode('ascii','ignore'),
        'vc_cluster'            : comps['vsphere_cluster'].encode('ascii','ignore'),
        'vc_host'               : attrs_json[0]['vcenter_host'].encode('ascii','ignore'),
        'vc_password'           : attrs_json[0]['vcenter_password'].encode('ascii','ignore'),
        'vc_user'               : attrs_json[0]['vcenter_username'].encode('ascii','ignore'),
    }
    complist.append(compute)

vcenter = {
    'vcenter': {
      'esxi_vlan_interface' : "",
      'computes'            : complist,
    },
}

path = '/var/lib/fuel/keys/{CLUSTER}/vmware.yaml'

with open(path.format(CLUSTER = sys.argv[1]), 'w') as outfile:
    outfile.write(yaml.dump(vcenter))
