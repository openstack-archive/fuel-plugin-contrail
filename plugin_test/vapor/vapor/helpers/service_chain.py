# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import re

from stepler import config as stepler_config
from stepler.third_party import waiter

from vapor import settings


def check_service_instance_ready(contrail_api_client, service_instance,
                                 server_steps):
    """Check that service instance creates nova server and it's booted."""

    def _get_virtual_machine_uuid():
        fresh_instance = contrail_api_client.service_instance_read(
            id=service_instance.uuid)
        refs = fresh_instance.get_virtual_machine_back_refs()
        if refs:
            return refs[0]['uuid']

    server_uuid = waiter.wait(
        _get_virtual_machine_uuid,
        timeout_seconds=settings.SERVICE_INSTANCE_CREATE_TIMEOUT)

    server = next(server for server in server_steps.get_servers()
                  if server.id == server_uuid)

    server_steps.check_server_status(
        server,
        expected_statuses=[stepler_config.STATUS_ACTIVE],
        transit_statuses=[stepler_config.STATUS_BUILD],
        timeout=stepler_config.SERVER_ACTIVE_TIMEOUT)

    def _check_record_in_log():
        server.get()
        console = server.get_console_output()
        return re.search(settings.SERVICE_INSTANCE_BOOT_DONE_PATTERN, console)

    waiter.wait(
        _check_record_in_log,
        timeout_seconds=settings.SERVICE_INSTANCE_BOOT_TIMEOUT)


def delete_service_instance(contrail_api_client, service_instance,
                            server_steps):
    """"Delete service instance."""
    refs = service_instance.get_virtual_machine_back_refs()
    contrail_api_client.service_instance_delete(id=service_instance.uuid)
    if refs:
        server_uuid = refs[0]['uuid']
        server = next(server for server in server_steps.get_servers()
                      if server.id == server_uuid)
        server_steps.check_server_presence(
            server,
            present=False,
            timeout=stepler_config.SERVER_DELETE_TIMEOUT)
