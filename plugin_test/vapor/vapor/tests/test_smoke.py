from hamcrest import assert_that, empty


def test_contrail_node_services_status(contrail_nodes, os_faults_steps):
    cmd = 'contrail-status | grep contrail'
    broken_services = []
    for node_result in os_faults_steps.execute_cmd(contrail_nodes, cmd):
        for line in node_result.payload['stdout_lines']:
            line = line.strip()
            name, status = line.split(None, 1)
            if status not in {'active', 'backup'}:
                err_msg = "{node}:{service} - {status}".format(node=node_result.host, service=name, status=status)
                broken_services.append(err_msg)
    assert_that(broken_services, empty())
