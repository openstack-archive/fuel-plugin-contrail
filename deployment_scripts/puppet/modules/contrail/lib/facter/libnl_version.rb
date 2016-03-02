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

require 'facter'
require 'puppet'

version = nil

pkg = Puppet::Type.type(:package).new(:name => 'libnl-3-200')
v = pkg.retrieve[pkg.property(:ensure)].to_s
version=v unless ["purged", "absent"].include?(v)

Facter.add("libnl_version") do
  setcode do
    version
  end
end
