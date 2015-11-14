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
class contrail::vip {

# Configuration files for HAProxy
  file {'/etc/haproxy/conf.d/095-rabbit_for_contrail.cfg':
    ensure  => present,
    content => template('contrail/095-rabbit_for_contrail.cfg.erb'),
    notify  => Service['haproxy'],
  }
  file {'/etc/haproxy/conf.d/096-vip_for_contrail.cfg':
    ensure  => present,
    content => template('contrail/096-vip_for_contrail.cfg.erb'),
    notify  => Service['haproxy'],
  }
  
# Services
  service {'haproxy':
    ensure     => running,
    name       => 'p_haproxy',
    hasstatus  => true,
    hasrestart => true,
    provider   => 'pacemaker',
    subscribe  => [File['/etc/haproxy/conf.d/095-rabbit_for_contrail.cfg'],
                  File['/etc/haproxy/conf.d/096-vip_for_contrail.cfg'],
                  ]
  }

}
