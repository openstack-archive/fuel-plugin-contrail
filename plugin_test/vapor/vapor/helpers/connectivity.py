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
from stepler.third_party import waiter


def check_tcp_connection_status(ip,
                                remote,
                                port=22,
                                must_available=True,
                                timeout=0):
    """Check TCP port connection availability (or not).

    Note:
        This method doesn't work on ubuntu-based servers due another `nc`
        variant.

    Args:
        ip (str): IP address to check connectivity to.
        remote (obj): Connected instance of
            'stepler.third_party.ssh.SshClient'.
        port (int, optional): TCP port to check.
        must_available (bool, optional): Flag whether port should be available
            or not.
        timeout (int, optional): Time in seconds to wait expected port
            condition.
    """

    def _predicate():
        result = remote.execute('nc -w1 {ip} {port} -e true'.format(
            ip=ip, port=port))
        return waiter.expect_that(result.exit_code == 0, is_(must_available))

    return waiter.wait(_predicate, timeout_seconds=timeout)
