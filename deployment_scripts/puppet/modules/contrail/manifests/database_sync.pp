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

class contrail::database_sync {

  if roles_include($contrail::contrail_controller_roles) {
    $cassandra_seeds    = $contrail::primary_contrail_controller_ip
  } elsif roles_include($contrail::analytics_db_roles) {
    $cassandra_seeds    = $::contrail::analytics_db_ips
  }

  $cassandra_seed = $cassandra_seeds[0]
  exec { 'wait_for_cassandra_seed':
    provider  => 'shell',
    command   => "nodetool status|grep ^UN|grep ${cassandra_seed}",
    tries     => 10, # wait for whole cluster is up: 10 tries every 30 seconds = 5 min
    try_sleep => 30,
  }

  exec { 'wait_for_cassandra':
    provider  => 'shell',
    command   => "nodetool status|grep ^UN|grep ${contrail::address}",
    tries     => 10, # wait for whole cluster is up: 10 tries every 30 seconds = 5 min
    try_sleep => 30,
    require   => Exec['wait_for_cassandra_seed']
  }
}

