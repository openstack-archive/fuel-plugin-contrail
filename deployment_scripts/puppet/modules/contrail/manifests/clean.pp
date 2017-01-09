#    Copyright 2015 Mirantis, Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

class contrail::clean {

  if !defined(Nova_config['DEFAULT/service_neutron_metadata_proxy']) {
    nova_config { 'DEFAULT/service_neutron_metadata_proxy' : ensure => absent }
  }

  if !defined(Nova_config['DEFAULT/neutron_url_timeout']) {
    nova_config { 'DEFAULT/neutron_url_timeout' : ensure => absent }
  }

  if !defined(Nova_config['neutron/url_timeout']) {
    nova_config { 'neutron/url_timeout' : ensure => absent }
  }
}
