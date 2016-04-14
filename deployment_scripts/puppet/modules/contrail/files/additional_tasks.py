from fabfile.utils.fabos import *
from fabric.contrib.files import exists

from fabfile.tasks.install import install_pkg_node
from fabfile.tasks.install import create_install_repo_node
from fabfile.tasks.install import apt_install


@task
@parallel(pool_size=20)
#use compute role because in testbed we will set conly ContrailVM ips
@roles('compute')
def prepare_contrailvm(pkg):
    """Install local repository of contrail packages on ContrailVM"""
    with settings(password='c0ntrail123', connection_attempts=10):
        execute(install_pkg_node, pkg, env.host_string)
        execute(create_install_repo_node, env.host_string)
        vrouter_pkg = ['contrail-vrouter-dkms', 'contrail-vrouter-common', 'contrail-nova-vif']
        apt_install(vrouter_pkg)
