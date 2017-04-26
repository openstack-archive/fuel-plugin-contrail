# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License

from kazoo import client
from vapor import settings
import pytest


@pytest.fixture
def zoo_client(nodes_ips):
    hosts_list = []
    contrail_controllers_fqdns = settings.CONTRAIL_ROLES_DISTRIBUTION[
        settings.ROLE_CONTRAIL_CONTROLLER]
    for name in nodes_ips:
        if name in contrail_controllers_fqdns:
            hosts_list.append("{}:{}".format(nodes_ips[name][0],
                                             settings.ZOOKEEPER_PORT))
    return client.KazooClient(hosts=','.join(hosts_list))


@pytest.fixture
def znodes_list(zoo_client):
    zk = zoo_client
    zk.start()
    znodes_list_ = zk.get_children("/")
    zk.stop()
    zk.close()
    return znodes_list_
