import subprocess


from fuelweb_test import logger


class BridgeCTL(object):
    """Vmrun utilite wrapper."""

    def __init__(self):
        """Create Bridge object."""
        super(BridgeCTL, self).__init__()

    def __execute(self, command):
        """Execute command.

        :param command: type string
        """
        command_to_run = 'sudo /sbin/brctl ' + command
        logger.info('{}'.format(command_to_run))
        subprocess.check_call(command_to_run, shell=True)

    def __run_process(self, command):
        """Execute command.

        :param command: type string
        """
        command_to_run = 'sudo /sbin/brctl ' + command
        logger.info('{}'.format(command_to_run))
        process = subprocess.Popen(
                command_to_run, stdout=subprocess.PIPE,
                stderr=subprocess.PIPE, shell=True)
        return process

    def add_interface(self, bridge_name, interface):
        """Add interface to bridge"""
        self.__execute('addif {0} {1}'.format(bridge_name, interface))

    def delete_interface(self, bridge_name, interface):
        """Delete interface from bridge"""
        self.__execute('delif {0} {1}'.format(bridge_name, interface))

    def stp(self, bridge_name, state='on'):
        """Turn stp on/off"""
        self.__execute('stp {0} {1}'.format(bridge_name, state))

    def get_interfaces_list(self, bridge_name):
        "Return interfaces list for bridge"
        p = self.__run_process('show {0}'.format(bridge_name))
        interfaces = p.stdout.read().split()[11:]
        return interfaces
