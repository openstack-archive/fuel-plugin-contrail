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


require 'yaml'

module Puppet::Parser::Functions
  newfunction(:add_data_to_yaml, :type => :rvalue, :doc => <<-EOS
    Append yaml file with additional data
    example:
      add_data_to_yaml(file, key, value)
    EOS
  ) do |args|

    file_path = args[0]
    key = args[1]
    value = args[2]

    yaml_string = File.read file_path
    current_data = YAML.load yaml_string
    current_data[key] = value
    yaml_string = YAML.dump current_data
    File.write(file_path, yaml_string)

    return current_data

  end
end

