import subprocess


from fuelweb_test import logger


class IP(object):
    """Vmrun utilite wrapper."""

    def __init__(self):
        """Create ip utilite object."""
        super(IP, self).__init__()

    def __execute(self, command):
        """Execute command.

        :param command: type string
        """
        command_to_run = 'sudo /sbin/ip ' + command
        logger.info('{}'.format(command_to_run))
        subprocess.check_call(command_to_run, shell=True)

    def __run_process(self, command):
        """Execute command.

        :param command: type string
        """
        command_to_run = 'sudo /sbin/ip ' + command
        logger.info('{}'.format(command_to_run))
        process = subprocess.Popen(
                command_to_run, stdout=subprocess.PIPE,
                stderr=subprocess.PIPE, shell=True)
        return process

    def set_link(self, device_name, state='up'):
        """Set link up on device."""
        self.__execute('link set dev {} up'.format(device_name))

    def add_ip_address(self, device_name, ip):
        """Add ip address to device."""
        self.__execute('addr add {0} dev {1}'.format(ip, device_name))

    def delete_ip_address(self, device_name, ip):
        """Remove ip address from device."""
        self.__execute('addr del dev {0} {1}'.format(device_name, ip))

    def get_interface_by_ip(self, ip):
        """Get interface by ip address."""
        p = self.__run_process('-o addr show to {}'.format(ip))
        interface = [
            line.split(' ')[1] for line in iter(p.stdout.readline, '')]
        return interface
