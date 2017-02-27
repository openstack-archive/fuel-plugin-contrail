"""Assertion helpers."""

# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import xml.etree.ElementTree as ET


def get_vna_vn(session, ip, port, network_fq_name):
    """Return a dict with network parameter on agent or None."""
    response = session.get(
        'http://{ip}:{port}/Snh_VnListReq?name={name}'.format(
            ip=ip, port=port, name=network_fq_name))
    response.raise_for_status()
    tree = ET.fromstring(response.content)
    networks = tree.findall('.//list/VnSandeshData')

    for network in networks:
        if network.find('name').text in network_fq_name:
            return {el.tag: el.text for el in network}
