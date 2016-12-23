"""`contrail-status` CLI command results parser."""
import re

from hamcrest import assert_that, empty  # noqa H301

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
            results[name] = status
    return results


def check_services_statuses(os_faults_steps, nodes):
    """Function to check that all contrail services are ok on nodes."""
    broken_services = []
    for node_result in os_faults_steps.execute_cmd(nodes, "contrail-status"):
        services_statuses = parse_result(node_result.payload['stdout_lines'])
        for name, status in services_statuses.items():
            if status not in GOOD_STATUSES:
                err_msg = "{node}:{service} - {status}".format(
                    node=node_result.host,
                    service=name,
                    status=status)
                broken_services.append(err_msg)
    assert_that(broken_services, empty())
