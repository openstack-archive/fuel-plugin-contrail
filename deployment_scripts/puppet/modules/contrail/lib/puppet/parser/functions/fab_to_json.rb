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
newfunction(:fab_to_json, :type => :rvalue, :doc => <<-EOS
    Convert string with fabric python data object to json
    EOS
  ) do |args|
	json = `python - <<-EOF
	import yaml, json
	with open('/etc/astute.yaml', 'r') as f:
	    data = yaml.load(f)['contrail']['contrail_vcenter_esxi_for_fabric']
	    esxi_dict = eval(data.split('=')[1])
	    json = json.dumps(esxi_dict)
	    print json
	EOF`
    return json
    end
end
