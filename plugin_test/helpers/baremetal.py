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

import subprocess
from fuelweb_test import logger
from devops.helpers.helpers import Environment
from devops.driver.ipmi.ipmi_driver import DevopsDriver as IPMIDriver

class BMDriver(object):
    def __init__(self, ipmi_user, ipmi_password, ipmi_host, remote_ip):
        self.env = Environment()
        self.remote_ip = remote_ip
        self.ipmi_drv = IPMIDriver(ipmi_user,
                                   ipmi_password,
                                   ipmi_host)

    def bm_reboot(self):
        self.ipmi_drv.node_reboot()

    def add_bridge_interface(self, interface_name, bridge_name):
        bm_ssh = self.env.get_ssh_to_remote(self.remote_ip)
        logger.info("BM IP: '{0}' Attach interface '{1}'"
                    " to the bridge '{2}'".format(self.remote_ip,
                                                  interface_name,
                                                  bridge_name))
        command = "sudo brctl addif {0} {1}".format(bridge_name,
                                                    interface_name)
        res = bm_ssh.execute(command)
        return res

    def del_bridge_interface(self, interface_name, bridge_name):
        bm_ssh = self.env.get_ssh_to_remote(self.remote_ip)
        logger.info("BM IP: '{0}' Detach interface '{1}'"
                    " to the bridge '{2}'".format(self.remote_ip,
                                                  interface_name,
                                                  bridge_name))
        command = "sudo brctl delif {0} {1}".format(bridge_name,
                                                    interface_name)
        res = bm_ssh.execute(command)
        return res
