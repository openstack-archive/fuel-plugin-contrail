import time
from fabfile.utils.fabos import *
from fabric.contrib.files import exists

from fabfile.tasks.install import install_pkg_node
from fabfile.tasks.install import create_install_repo_node
from fabfile.tasks.install import apt_install


@task
#@parallel(pool_size=20)
#use compute role because in testbed we will set conly ContrailVM ips
@roles('compute')
def prepare_contrailvm(pkg):
    """Install local repository of contrail packages on ContrailVM"""
    time.sleep(30)
    with settings(password='c0ntrail123', connection_attempts=10):
        sudo('echo > /etc/apt/sources.list')
        execute(install_pkg_node, pkg, env.host_string)
        execute(create_install_repo_node, env.host_string)


@task
#@parallel(pool_size=20)
#use compute role because in testbed we will set conly ContrailVM ips
@roles('compute')
def fab_install_vrouter():
    """Install vrouter packages on ContrailVM"""
    with settings(password='c0ntrail123', connection_attempts=10):
        vrouter_pkg = ['contrail-vrouter-dkms', 'contrail-vrouter-common', 'contrail-nova-vif']
        apt_install(vrouter_pkg)


@task
@parallel(pool_size=20)
def disable_add_vnc_config():
    """Disable provision vrouter when exucute setup-vnc-compute on ContrailVM.
       On ContrailVMs we don't have access to managment network, so we don't have access to keystone."""
    with settings(password='c0ntrail123', connection_attempts=20):
        patched_file = '/usr/local/lib/python2.7/dist-packages/contrail_provisioning/compute/common.py'
        cmd = 'sed -i "s~python\ /opt/contrail/utils/provision_vrouter\.py~echo~g" %s' % patched_file
        sudo(cmd)


@task
def provision_contrailvm(cmd):
    """Create configuration files on ContrailVM"""
    with settings(password='c0ntrail123', connection_attempts=10):
        sudo(cmd)


@task
def change_hostname(hostname):
    """Change hostname on ContrailVM"""
    with settings(password='c0ntrail123', connection_attempts=10):
        cmd = 'echo %s > /etc/hostname' % hostname
        sudo(cmd)


@task
def set_ntp(ntp):
    """Set proper ntp server on ContrailVM"""
    with settings(password='c0ntrail123', connection_attempts=10):
        sudo('sed -i "/^server/g" /etc/ntp.conf')
        sudo('echo "server %s" >> /etc/ntp.conf' % ntp)
