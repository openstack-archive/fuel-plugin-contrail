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
  newfunction(:sriov_in_kernel, :type => :rvalue, :doc => <<-EOS
    Returns true if sriov enable in kernel
    example:
      sriov_in_kernel()
    EOS
  ) do |args|
    params = File.read("/proc/cmdline")
    if params.include? "intel_iommu=on" and params.include? "iommu=pt"
      return true
    else
      return false
    end

  end
end

