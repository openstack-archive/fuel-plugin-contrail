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

class contrail::controller::scheduler {

  if $contrail::global_dpdk_enabled {
    ini_subsetting {'add_aggregateinstanceextraspecsfilter':
      ensure             => present,
      section            => 'DEFAULT',
      key_val_separator  => '=',
      path               => '/etc/nova/nova.conf',
      setting            => 'scheduler_default_filters',
      subsetting         => 'AggregateInstanceExtraSpecsFilter',
      subsetting_separator => ',',
      notify             => Service['nova-scheduler'],
    }
  }

  if $contrail::settings['dpdk_on_vf'] {
    ini_subsetting {'add_pci_passthrough_filter':
      ensure             => present,
      section            => 'DEFAULT',
      key_val_separator  => '=',
      path               => '/etc/nova/nova.conf',
      setting            => 'scheduler_default_filters',
      subsetting         => 'PciPassthroughFilter',
      subsetting_separator => ',',
      notify             => Service['nova-scheduler'],
    }
  }

  Ini_subsetting <||> ~>
  service { 'nova-scheduler':
    ensure    => $ensure,
    enable    => $enabled,
    hasstatus => true,
  }
}
