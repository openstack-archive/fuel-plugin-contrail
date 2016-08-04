"""Copyright 2016 Mirantis, Inc.

Licensed under the Apache License, Version 2.0 (the "License"); you may
not use this file except in compliance with the License. You may obtain
copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
License for the specific language governing permissions and limitations
under the License.
"""
import paramiko
import time

from devops.helpers.helpers import wait
from fuelweb_test import logger


class SSH(object):
    """Paramiko ssh client wrapper.

    :param ip: string, host ip to connect to
    :param username: string, a username to use for authentication
    :param userpassword: string, a password to use for authentication
    :param timeout: timeout (in seconds) for the TCP connection
    :param port: host port to connect to
    """

    result = {
        'stdout': [],
        'stderr': [],
        'exit_code': 0
    }
    instance_creds = ('cirros', 'cubswin:)')

    def __init__(self, ip, username=instance_creds[0],
                 userpassword=instance_creds[1], timeout=30, port=22):
        """Create SshClient object.

        :param ip: string, host ip to connect to
        :param username: string, a username to use for authentication
        :param userpassword: string, a password to use for authentication
        :param timeout: timeout (in seconds) for the TCP connection
        :param port: host port to connect
        """
        self.ip = ip
        self.username = username
        self.userpassword = userpassword
        self.timeout = timeout
        self.port = port

    def __enter__(self):
        """Create ssh conection."""
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh.connect(
            self.ip, port=self.port, username=self.username,
            password=self.userpassword, timeout=self.timeout
        )
        return self

    def __exit__(self, exc_type, value, traceback):
        """Close ssh conection."""
        self.ssh.close()

    def remote_execute_command(self, remote_ip, user, password,
                               command, wait=30):
        """Check execute remote command.

        :param  remote_ip: string, instance ip connect to
        :param user: string, a username to use for authentication
        :param password: string, a password to use for authentication
        :param command: string, remote command
        :param wait: integer, time to wait available ip of instances
        """
        interm_transp = self.ssh.get_transport()
        time.sleep(wait)
        interm_chan = interm_transp.open_channel('direct-tcpip',
                                                 (remote_ip, 22),
                                                 (self.ip, 0))
        transport = paramiko.Transport(interm_chan)
        transport.start_client()
        logger.info("Passing authentication to VM")
        transport.auth_password(user, password)
        channel = transport.open_session()
        channel.get_pty()
        channel.fileno()
        channel.exec_command(command)
        logger.debug("Receiving exit_code")
        self.result['exit_code'] = channel.recv_exit_status()
        logger.debug("Receiving stdout")
        self.result['stdout'] = channel.recv(1024)
        logger.debug("Receiving stderr")
        self.result['stderr'] = channel.recv_stderr(1024)
        logger.debug("Closing channel")
        channel.close()

        return self.result

    def check_connection_through_host(self, ip_pair, user=instance_creds[0],
                                      password=instance_creds[1],
                                      command='pingv4',
                                      result_of_command=0, timeout=30,
                                      interval=5):
        """Check network connectivity between instances.

        :param ip_pair: type list,  ips of instances
        :param user: string, a username to use for authentication
        :param password: string, a password to use for authentication
        :param command: type string, key from dictionary 'commands'
                        by default is 'pingv4'
        :param  result_of_command: type interger, exite code of command
                                   execution by default is 0
        :param timeout: wait to get expected result
        :param interval: interval of executing command
        """
        commands = {
            "pingv4": "ping -c 5 {}",
            "pingv6": "ping6 -c 5 {}",
            "arping": "sudo arping -I eth0 {}"}

        for ip_from in ip_pair:
            for ip_to in ip_pair[ip_from]:
                message = self.generate_message(
                    commands[command], result_of_command, ip_from, ip_to)
                wait(
                    lambda:
                    self.remote_execute_command(
                        ip_from, user, password,
                        commands[command].format(ip_to),
                        wait=timeout)['exit_code'] == result_of_command,
                    interval=interval,
                    timeout=timeout,
                    timeout_msg=message.format(
                        ip_from, ip_to)
                )

    def generate_message(self, command, result_of_command, ip_from, ip_to):
        """Generate error message for check connection methods.

        :param command: type string, name of command
        :param result_of_command: type interger, exite code of
                                  command execution
        :param ip_from: type string, check connection from 'ip_from'
        :param ip_to: type string, check connection from 'ip_to'
        """
        if result_of_command == 0:
            param = "isn't"
        else:
            param = "is"
        message = "{0} {1} available from {2} to {3}".format(
            command, param, ip_from, ip_to)
        return message
