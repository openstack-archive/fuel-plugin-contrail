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

# This facter returns the version and build for the python-contrail package.
# It may be used to detect a version of contrail used in the environment.

require 'hiera'
require 'puppet'
require 'puppet/util/inifile'

Facter.add("supervisor_params") do
  setcode do
    res = []
    vrouter_config  = '/etc/contrail/supervisord_vrouter_files/contrail-vrouter-dpdk.ini'
    vrouter_section = 'program:contrail-vrouter-dpdk'
    if File.exist?(vrouter_config)
      file  = Puppet::Util::IniConfig::PhysicalFile.new(vrouter_config)
      file.read
      config_vrouter_params = file.get_section(vrouter_section)['command'].split('--no-daemon')[-1].strip
      res << config_vrouter_params
    end

    res.join(' ') if res
  end
end
