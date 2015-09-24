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

include contrail

if $contrail::node_name =~ /^contrail.\d+$/ {
  # TODO(mrostecki): Create module for logging in osnailyfacter and include it
  # here.
  $base_syslog_hash = hiera('base_syslog_hash')
  $syslog_hash      = hiera('syslog_hash')
  $use_syslog       = hiera('use_syslog', true)
  $debug            = hiera('debug', false)

  $base_syslog_rserver  = {
    'remote_type' => 'tcp',
    'server' => $base_syslog_hash['syslog_server'],
    'port' => $base_syslog_hash['syslog_port']
  }

  $syslog_rserver = {
    'remote_type' => $syslog_hash['syslog_transport'],
    'server' => $syslog_hash['syslog_server'],
    'port' => $syslog_hash['syslog_port'],
  }

  if ($syslog_hash['syslog_server'] != ''
      and $syslog_hash['syslog_port'] != ''
      and $syslog_hash['syslog_transport'] != '') {
    $rservers = [$base_syslog_rserver, $syslog_rserver]
  } else {
    $rservers = [$base_syslog_rserver]
  }

  if $use_syslog {
    class { '::openstack::logging':
      role             => 'client',
      show_timezone    => true,
      # log both locally include auth, and remote
      log_remote       => true,
      log_local        => true,
      log_auth_local   => true,
      # keep four weekly log rotations,
      # force rotate if 300M size have exceeded
      rotation         => 'weekly',
      keep             => '4',
      minsize          => '10M',
      maxsize          => '100M',
      # remote servers to send logs to
      rservers         => $rservers,
      # should be true, if client is running at virtual node
      virtual          => str2bool($::is_virtual),
      # Rabbit doesn't support syslog directly
      rabbit_log_level => 'NOTICE',
      debug            => $debug,
    }
  }
}
