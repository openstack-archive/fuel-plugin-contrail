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

class contrail::contrail_webui(
  $deployment_id = hiera('deployment_id'),
  $master_ip     = hiera('master_ip'),
  $link          = "https://${::contrail::mos_public_vip}:8143/"
  )
{

  $text = "Dashboard for Contrail Web UI: ${link}"
  $contrail_link_data = "{\"title\":\"ContrailUI\",\
  \"description\":\"${text}\",\
  \"url\":\"${link}\"}"
  $contrail_link_created_file = '/etc/contrail/fuel_link_created'

  exec { 'notify_contrail_url':
    creates => $contrail_link_created_file,
    command => "/usr/bin/curl -sL -w \"%{http_code}\" \
  -H 'Content-Type: application/json' -X POST -d '${contrail_link_data}' \
  http://${master_ip}:8000/api/clusters/${deployment_id}/plugin_links \
  -o /dev/null | /bin/grep 201 && /usr/bin/touch ${contrail_link_created_file}",
  }

}