# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from hamcrest import assert_that, contains_string
from pycontrail import types
from stepler import config as stepler_config


def test_subnet_creating_with_custom_ipam(
        contrail_api_client, contrail_ipam, contrail_network,
        contrail_create_subnet, cirros_image, flavor, security_group,
        server_steps, port_steps, create_floating_ip, public_network):
    """Check creating subnet with custom IPAM.

    Steps:
        #. Create IPAM
        #. Create network
        #. Add IPAM subnet to network
        #. Boot an instance on network
        #. Assign floating IP to instance
        #. Check that instance is SSH accessible
    """
    contrail_create_subnet(contrail_network, contrail_ipam)
    server = server_steps.create_servers(
        image=cirros_image,
        flavor=flavor,
        security_groups=[security_group],
        nics=[{
            'net-id': contrail_network.uuid
        }],
        username=stepler_config.CIRROS_USERNAME,
        password=stepler_config.CIRROS_PASSWORD)[0]
    server1_port = port_steps.get_port(
        device_owner=stepler_config.PORT_DEVICE_OWNER_SERVER,
        device_id=server.id)
    floating_ip = create_floating_ip(public_network, port=server1_port)
    ssh = server_steps.get_server_ssh(
        server, ip=floating_ip['floating_ip_address'])
    assert_that(ssh.check(), "Server is unavailable with SSH")


def test_ipam_virtual_dns(
        contrail_dns, contrail_ipam, contrail_network, contrail_create_subnet,
        add_dns_record, contrail_api_client, security_group, server_steps,
        cirros_image, flavor, port_steps, create_floating_ip, public_network):
    """Check IPAM with Virtual DNS.

    Steps:
        #. Create virtual DNS
        #. Create IPAM
        #. Add DNS records
        #. Bind DNS to IPAM
        #. Create network with IPAM
        #. Boot nova server on network
        #. Check that `nslookup` on server works with Virtual DNS
    """
    # Create DNS records
    ip = '1.2.3.4'
    name = 'test.example.com'
    add_dns_record(contrail_dns, r_name=name, r_data=ip)

    # Add DNS to IPAM
    contrail_ipam.network_ipam_mgmt = types.IpamType(
        ipam_dns_method='virtual-dns-server',
        ipam_dns_server=types.IpamDnsAddressType(
            virtual_dns_server_name=':'.join(contrail_dns.fq_name)))
    contrail_api_client.network_ipam_update(contrail_ipam)

    # Create subnet
    contrail_create_subnet(contrail_network, contrail_ipam)
    # Boot server
    server = server_steps.create_servers(
        image=cirros_image,
        flavor=flavor,
        security_groups=[security_group],
        nics=[{
            'net-id': contrail_network.uuid
        }],
        username=stepler_config.CIRROS_USERNAME,
        password=stepler_config.CIRROS_PASSWORD)[0]
    server1_port = port_steps.get_port(
        device_owner=stepler_config.PORT_DEVICE_OWNER_SERVER,
        device_id=server.id)
    floating_ip = create_floating_ip(public_network, port=server1_port)
    with server_steps.get_server_ssh(
            server, ip=floating_ip['floating_ip_address']) as server_ssh:
        result = server_ssh.execute('nslookup ' + name)
    assert_that(result.stdout, contains_string(ip))
