"""`contrail-status` CLI command results parser."""
import collections
import re

from hamcrest import assert_that, empty  # noqa H301

GOOD_STATUSES = {'active', 'backup'}


def parse_result(stdout_lines):
    """Function to parse result of `contrail-status`.

    It returns a dict:
        {'section name': {'service': 'status', 'service', 'status', ...},
         'section2_name': {...},
         ...}
    """
    service_pattern = re.compile(r'(?P<name>[^\s]+)\s+(?P<status>.+)')
    results = collections.defaultdict(dict)
    section = None
    for line in stdout_lines:
        line = line.strip()
        if not line:
            section = None
        if '==' in line:
            section = line.strip("= ")
            continue
        service_result = service_pattern.search(line)
        if service_result:
            assert section, 'No section founded for service in output'
            results[section] = dict((service_result.groups(), ))
    return results


def check_services(os_faults_steps, nodes):
    """Function to check that all contrail services are ok on nodes."""
    broken_services = []
    for node_result in os_faults_steps.execute_cmd(nodes, "contrail-status"):
        services_statuses = parse_result(node_result.payload['stdout_lines'])
        for section, services in services_statuses.items():
            for name, status in services.items():
                if status not in GOOD_STATUSES:
                    err_msg = "{node}:{section}:{service} - {status}".format(
                        node=node_result.host,
                        service=name,
                        status=status,
                        section=section)
                    broken_services.append(err_msg)
    assert_that(broken_services, empty())
