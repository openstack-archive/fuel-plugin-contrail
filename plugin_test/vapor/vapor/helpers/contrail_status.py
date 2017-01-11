"""`contrail-status` CLI command results parser."""
import re

from hamcrest import assert_that, empty, has_entries  # noqa H301
from six import moves
from stepler.third_party import waiter

GOOD_STATUSES = {'active', 'backup'}


def parse_result(stdout_lines):
    """Function to parse result of `contrail-status`.

    It returns a dict:
        {'service': 'status', 'service', 'status', ...}
    """
    service_pattern = re.compile(r'(?P<name>[^\s]+)\s+(?P<status>.+)')
    results = {}
    for line in stdout_lines:
        line = line.strip()
        if not line or '==' in line:
            continue
        service_result = service_pattern.search(line)
        if service_result:
            name, status = service_result.groups()
            if ':' in name:
                name = name.split(':')[0]
            results[name] = status
    return results


def get_services_statuses(os_faults_steps):
    """Function to retrieve contrail services statuses on each node.

    It returns a dict:
        {'node-1.test.domain.local': {'service1': 'status',
                                      'service2': 'status'},
         'node-2.test.domain.local': {...},
         ...}
    """
    cmd = 'contrail-status'
    nodes = os_faults_steps.get_nodes_by_cmd('which ' + cmd)
    results = {}
    for node_result in os_faults_steps.execute_cmd(nodes, cmd):
        node = next(moves.filter(lambda x: x.ip == node_result.host, nodes))
        services_statuses = parse_result(node_result.payload['stdout_lines'])
        results[node.fqdn] = services_statuses

    return results


def check_services_statuses(os_faults_steps):
    """Function to check that all contrail services are ok on nodes."""
    broken_services = []
    for fqdn, services in get_services_statuses(os_faults_steps).items():
        for name, status in services.items():
            if status not in GOOD_STATUSES:
                err_msg = "{node}:{service} - {status}".format(
                    node=fqdn, service=name, status=status)
                broken_services.append(err_msg)
    assert_that(broken_services, empty())


def check_service_status(os_faults_steps,
                         nodes_fqdns,
                         service,
                         expected_status,
                         timeout=0):
    """Check that service on nodes_fqdns has expected status."""

    def predicate():
        statuses = get_services_statuses(os_faults_steps)
        return waiter.expect_that(statuses,
                                  has_entries(**{
                                      node: has_entries({
                                          service: expected_status
                                      })
                                      for node in nodes_fqdns
                                  }))

    waiter.wait(predicate, timeout_seconds=timeout)
