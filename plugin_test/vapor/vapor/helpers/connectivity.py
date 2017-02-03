# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from hamcrest import is_
from stepler.third_party import ping
from stepler.third_party import waiter

CONNECTED = 'CONNECTED'


def check_connection_status(ip,
                            remote,
                            port=22,
                            udp=False,
                            answer=CONNECTED,
                            must_available=True,
                            timeout=0):
    """Check TCP/UDP port connection availability (or not).

    Note:
        This method doesn't work on ubuntu-based servers due another `nc`
        variant.
        UDP checking requires an server on remote side. Simple server example:
        ```while true; do nc -u -l -p 1235 -e echo Reply; done```

    Args:
        ip (str): IP address to check connectivity to.
        remote (obj): Connected instance of
            'stepler.third_party.ssh.SshClient'.
        port (int, optional): Port to check.
        udp (bool, optional): Check UDP instead of TCP
        must_available (bool, optional): Flag whether port should be available
            or not.
        timeout (int, optional): Time in seconds to wait expected port
            condition.
    """

    proto_flag = ''
    if udp:
        proto_flag = '-u'

    def _predicate():
        result = remote.execute(
            'echo "" | nc {proto} -w1 {ip} {port} | grep {answer}'.format(
                ip=ip, port=port, proto=proto_flag, answer=answer))
        msg = ("Expected that {proto} connection for {port}"
               " will be {status}").format(
                   proto='UDP' if udp else 'TCP',
                   port=port,
                   status='available' if must_available else 'unavailable')
        return waiter.expect_that(result.exit_code == 0,
                                  is_(must_available), msg)

    return waiter.wait(_predicate, timeout_seconds=timeout, sleep_seconds=2)


def check_icmp_connection_status(ip, remote, must_available=True, timeout=0):
    """Check that icmp connection to ip is `must_available`."""

    def predicate():
        ping_result = ping.Pinger(ip, remote=remote).ping(count=3)
        if must_available:
            value = ping_result.loss
        else:
            value = ping_result.received
        return waiter.expect_that(value, is_(0))

    return waiter.wait(predicate, timeout_seconds=timeout)


def start_port_listener(server_ssh, port, udp=False, answer=CONNECTED):
    """Start background netcat listener on remote server.

    Note:
        Netcat call syntax is valid only for cirros.
    """
    proto = '-u' if udp else ''
    listener_cmd = 'nc {proto} -l -p {port} -e echo "{answer}"'.format(
        proto=proto, port=port, answer=answer)

    loop_cmd = "while true; do {}; done".format(listener_cmd)

    server_ssh.background_call(loop_cmd)
