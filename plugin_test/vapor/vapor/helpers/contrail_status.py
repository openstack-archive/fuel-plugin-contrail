"""`contrail-status` CLI command results parser."""
import collections
import re

import attrdict
from hamcrest import (empty, has_entries, has_items, has_length)  # noqa: H301
from stepler.third_party import waiter

from vapor.helpers import asserts
from vapor.helpers import nodes_steps
from vapor import settings


STATUS_ACTIVE = 'active'
STATUS_BACKUP = 'backup'
STATUS_INACTIVE = 'inactive (disabled on boot)'


def parse_result(stdout_lines):
    """Function to parse result of `contrail-status`.

    It yields an AttrDict:
        {'service': 'service1',
         'status': 'active',
         'section':' Contrail Database'}
    """
    service_pattern = re.compile(r'(?P<name>[^\s]+)\s+(?P<status>.+)')
    section = None
    for line in stdout_lines:
        line = line.strip()
        if not line:
            continue
        if '==' in line:
            section = line.strip(' =')
            continue
        service_result = service_pattern.search(line)
        if service_result:
            name, status = service_result.groups()
            if ':' in name:
                name = name.split(':')[0]
            yield attrdict.AttrDict(
                service=name, status=status, section=section)


def get_services_statuses(os_faults_steps):
    """Function to retrieve contrail services statuses on each node.

    It returns an AttrDict:
        {'node-1.test.domain.local': [
            {'name': service1',
             'status': 'active',
             'section': 'Contrail Database'},
            {'name': service2',
             'status': 'active',
             'section': 'Contrail Database'},
            ]
         'node-2.test.domain.local': [...],
         ...}
    """
    cmd = 'contrail-status'
    nodes = os_faults_steps.get_nodes_by_cmd('which ' + cmd)
    results = collections.defaultdict(list)
    for node_result in os_faults_steps.execute_cmd(nodes, cmd):
        node = nodes_steps.get_node_by_result(node_result, os_faults_steps)
        for service in parse_result(node_result.payload['stdout_lines']):
            results[node.fqdn].append(service)

    return attrdict.AttrDict(results)


def check_services_statuses(os_faults_steps):
    """Function to check that all contrail services are ok on nodes."""
    services_data = collections.defaultdict(list)
    Status = collections.namedtuple('Status', ['node', 'status', 'section'])
    for fqdn, services in get_services_statuses(os_faults_steps).items():
        for service in services:
            status = Status(
                node=fqdn, status=service.status, section=service.section)
            services_data[service.service].append(status)

    with asserts.AssertsCollector() as collector:
        for service, statuses in services_data.items():
            err_msg = (
                "`{}` has instances with wrong statuses").format(service)

            statuses = set(statuses)
            active = {x for x in statuses if x.status == STATUS_ACTIVE}
            if service in settings.ACTIVE_BACKUP_SERVICES:
                backup = {x for x in statuses if x.status == STATUS_BACKUP}
                broken = statuses - active - backup
                collector.check(active,
                                has_length(1),
                                ('`{}` should have'
                                 ' only one active instance').format(service))
                collector.check(broken, empty(), err_msg)
            elif service == 'contrail-database':
                allowed_inactive = set()
                for status in statuses:
                    if (status.status == STATUS_INACTIVE and
                            status.section == 'Contrail Database'):
                        allowed_inactive.add(status)
                broken = statuses - active - allowed_inactive
                collector.check(broken, empty(), err_msg)
            else:
                broken = statuses - active
                collector.check(broken, empty(), err_msg)


def check_service_status(os_faults_steps,
                         nodes_fqdns,
                         service,
                         expected_status,
                         timeout=0):
    """Check that service on nodes_fqdns has expected status."""

    def predicate():
        services = get_services_statuses(os_faults_steps)
        return waiter.expect_that(
            services,
            has_entries(**{
                node: has_items(
                    has_entries(service=service, status=expected_status))
                for node in nodes_fqdns
            }))

    waiter.wait(predicate, timeout_seconds=timeout)
