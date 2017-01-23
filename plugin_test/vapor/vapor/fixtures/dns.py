# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from pycontrail import exceptions
import pycontrail.types as types
import pytest
from stepler import config as stepler_config
from stepler.third_party import utils


@pytest.fixture
def contrail_dns(contrail_api_client, default_domain):
    """Fixture to create contrail DNS."""
    name, = utils.generate_ids()
    dns_data = types.VirtualDnsType(
        domain_name='example.com',
        next_virtual_DNS=stepler_config.GOOGLE_DNS_IP,
        record_order='fixed',
        default_ttl_seconds=60 * 60)
    dns = types.VirtualDns(
        name, parent_obj=default_domain, virtual_DNS_data=dns_data)
    contrail_api_client.virtual_DNS_create(dns)

    yield dns

    try:
        contrail_api_client.virtual_DNS_delete(id=dns.uuid)
    except exceptions.NoIdError:
        pass


@pytest.fixture
def add_dns_record(contrail_api_client):
    """Callable fixture to add dns record."""
    records = []

    def _add_dns_record(dns,
                        r_name,
                        r_data,
                        r_type='A',
                        r_class='IN',
                        r_ttl_seconds=60 * 60,
                        record_name=None):
        record_name = record_name or next(utils.generate_ids())
        record = types.VirtualDnsRecord(
            name=record_name,
            parent_obj=dns,
            virtual_DNS_record_data=types.VirtualDnsRecordType(
                record_name=r_name,
                record_type=r_type,
                record_class=r_class,
                record_data=r_data,
                record_ttl_seconds=r_ttl_seconds))
        records.append(record)
        contrail_api_client.virtual_DNS_record_create(record)

    yield _add_dns_record

    for record in records:
        contrail_api_client.virtual_DNS_record_delete(id=record.uuid)
