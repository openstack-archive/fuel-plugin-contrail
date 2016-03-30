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

class contrail::compute::vmware {

  file{'/root/.ssh/authorized_keys':
    ensure => present,
    mode   => '0600',
  }

  file_line{'vmware pub authorized keys':
    path => '/root/.ssh/authorized_keys',
    line => file('/root/.ssh/vmware_id_rsa.pub')
  }

  # class { 'contrail::ssh':
  #   password_auth     => yes,
  #   permit_root_login => yes,
  # }

}
