from vapor.helpers import contrail_status


def test_contrail_database_status(os_faults_steps, contrail_db_nodes):
    contrail_status.check_services(os_faults_steps, contrail_db_nodes)
