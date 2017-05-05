# Project, contrail and OpenStack settings

import os
import sys
import yaml
import logbook

from stepler import config as stepler_config


LOG_FILENAME = './vapor.log'
logger = logbook.Logger(__name__)
logger.handlers.append(logbook.FileHandler(LOG_FILENAME,
                                           level='DEBUG',
                                           bubble=True))
logger.handlers.append(logbook.StreamHandler(sys.stderr,
                                             level='DEBUG',
                                             bubble=True))

BASE_DIR = os.path.dirname(__file__)

PATH_TO_CERT = '/tmp/cert.crt'
VERIFY_SSL = False
DISABLE_SSL = True
KEYSTONE_CREDS = {
    'username': 'admin',
    'password': 'secret',
    'tenant_name': 'admin',
}

CONTRAIL_CREDS = {'controller_addr': '192.168.1.127'}


CONTRAIL_API_URL = os.environ['CONTRAIL_API_URL']
CONTRAIL_ANALYTICS_URL = os.environ['CONTRAIL_ANALYTICS_URL']

NEUTRON_CONTRAIL_PLUGIN_CONFIG_PATH = (
    '/etc/neutron/plugins/opencontrail/ContrailPlugin.ini')

CONTRAIL_CONFIG_PATH = '/etc/contrail/'

# Time between poweroff and start contrail controller node
CONTRAIL_CONTROLLER_RESTART_TIMEOUT = 5 * 60

# Time between networks unplug and plug back to contrail controller node
CONTRAIL_CONTROLLER_NET_REPLUG_TIMEOUT = 5 * 60

# Time to wait database purge
DB_PURGE_TIMEOUT = 60 * 60

# Time to wait service status to be changed
SERVICE_STATUS_CHANGE_TIMEOUT = 60

# Time to wait until nova server will know about attached floating IP
FLOATING_IP_BIND_TIMEOUT = 30

# Time to applying new password on keystone
PASSWORD_CHANGE_TIMEOUT = 30

# Time to wait for success ping
PING_SUCCESS_TIMEOUT = 60 * 2

# Security group apply timeout
SECURITY_GROUP_APPLY_TIMEOUT = 20

# Time to wait for contrail agent cleanup after stopping control node
CONTRAIL_AGENT_CLEANUP_TIMEOUT = 20 * 60

# Time to wait for contrail agent vna vm list to contain server uuid
CONTRAIL_AGENT_VNA_VM_LIST_TIMEOUT = 3 * 60

# Time to wait for contrail to be operable after reset node
CONTRAIL_NODE_RESET_TIMEOUT = 5 * 60

ROLE_CONTRAIL_CONTROLLER = 'contrail-controller'
ROLE_CONTRAIL_ANALYTICS = 'contrail-analytics'
ROLE_CONTRAIL_DB = 'contrail-db'
ROLE_CONTRAIL_COMPUTE = 'contrail-compute'
ROLE_CONTRAIL_CONFIG = 'contrail-config'
ROLE_CONTRAIL_UI = 'contrail-ui'

CONTRAIL_ROLES_SERVICES_MAPPING = {
    ROLE_CONTRAIL_CONFIG: (
        'supervisor-config',
        'contrail-config-nodemgr', ),
    ROLE_CONTRAIL_CONTROLLER: (
        'supervisor-control',
        'contrail-control',
        'contrail-control-nodemgr',
        'contrail-dns',
        'contrail-named',
        'contrail-api',
        'contrail-device-manager',
        'contrail-discovery',
        'contrail-schema',
        'contrail-svc-monitor',
        'contrail-database',
        'supervisor-database',
        'contrail-database-nodemgr',
        'kafka', ),
    ROLE_CONTRAIL_ANALYTICS: (
        'supervisor-analytics',
        'contrail-alarm-gen',
        'contrail-analytics-api',
        'contrail-analytics-nodemgr',
        'contrail-collector',
        'contrail-query-engine',
        'contrail-snmp-collector',
        'contrail-topology', ),
    ROLE_CONTRAIL_DB: (
        'contrail-database',
        'supervisor-database',
        'contrail-database-nodemgr',
        'kafka', ),
    ROLE_CONTRAIL_COMPUTE: (
        'contrail-vrouter-agent',
        'supervisor-vrouter',
        'contrail-vrouter-nodemgr', ),
    ROLE_CONTRAIL_UI: (
        'supervisor-webui',
        'contrail-webui',
        'contrail-webui-middleware',
        'supervisor-support-service', ),
}

CONTRAIL_ROLES_DISTRIBUTION_YAML = os.environ.get(
    'CONTRAIL_ROLES_DISTRIBUTION_YAML',
    os.path.join(
        BASE_DIR, '../roles_mk22_qa_lab01.yaml'))

with open(CONTRAIL_ROLES_DISTRIBUTION_YAML) as f:
    CONTRAIL_ROLES_DISTRIBUTION = yaml.safe_load(f) or {}

CONTRAIL_CONNECTIONS = {
    ROLE_CONTRAIL_ANALYTICS: [
        'contrail-collector',
        'contrail-analytics-api',
        'contrail-query-engine',
    ],
    ROLE_CONTRAIL_CONFIG: [
        'DeviceManager',
        'contrail-schema',
        'contrail-svc-monitor',
        'contrail-api',
    ]
}

CONTRAIL_ANALYTIC_PROCESSES = {
    ROLE_CONTRAIL_CONFIG: [
        'contrail-discovery',
        'contrail-config-nodemgr',
        'contrail-svc-monitor',
        'contrail-api',
        'contrail-schema',
    ],
    ROLE_CONTRAIL_ANALYTICS: [
        'contrail-query-engine',
        'contrail-analytics-api',
        'contrail-collector',
        'contrail-analytics-nodemgr',
    ],
}

ACTIVE_BACKUP_SERVICES = ('contrail-svc-monitor',
                          'contrail-schema',
                          'contrail-device-manager')

HEAT_TEMPLATES_PATH = os.path.join(BASE_DIR, 'heat')

VROUTER_HEADLESS_MODE_CMD = r"grep -iP '^headless_mode\s*=\s*true' /etc/contrail/contrail-vrouter-agent.conf"  # noqa

ZOOKEEPER_PORT = 2181

ZOOKEEPER_NODES = ["api-server",
                   "consumers",
                   "svc-monitor",
                   "contrail_cs",
                   "device-manager",
                   "controller_epoch",
                   "lockpath",
                   "id",
                   "fq-name-to-uuid",
                   "admin",
                   "zookeeper",
                   "api-server-election",
                   "config",
                   "controller",
                   "schema-transformer",
                   "brokers"]

SERVER_ATTR_HYPERVISOR_HOSTNAME = 'OS-EXT-SRV-ATTR:hypervisor_hostname'

NEUTRON_SRIOV_NIC_AGENT = "neutron-sriov-nic-agent"

DPDK_NEC_BIND_CMD = 'curl https://raw.githubusercontent.com/Juniper/contrail-dpdk/master/tools/dpdk_nic_bind.py 2>/dev/null | python -'  # noqa

# SR-IOV
SRIOV_PHYSNET = os.environ.get('SRIOV_PHYSNET', 'physnet1')
SEGMENTATION_ID = int(os.environ.get('SEGMENTATION_ID', 2426))

# Security groups
INGRESS = 'ingress'
EGRESS = 'egress'

SECURITY_GROUP_PING_RULES = [
    {
        # ping IPv4
        'direction': INGRESS,
        'protocol': 'icmp',
        # For ICMP neutron allows to set port range from 0 to 255.
        # But in neutron this means ICMP type and ICMP code.
        # So this values are valid only with contrail.
        'port_range_min': 0,
        'port_range_max': 255,
        'remote_ip_prefix': '0.0.0.0/0',
    }
]

SECURITY_GROUP_SSH_PING_RULES = (stepler_config.SECURITY_GROUP_SSH_RULES +
                                 SECURITY_GROUP_PING_RULES)

DPDK_ENABLED_GROUP = u'Network devices using DPDK-compatible driver'



# Service chaining
# TODO(gdyuldin): relace with real URL
NAT_SERVICE_IMAGE_URL = os.environ.get('NAT_SERVICE_IMAGE_URL',
                                       '/home/jenkins/nat.qcow2')
SERVICE_INSTANCE_CREATE_TIMEOUT = 2 * 60
SERVICE_INSTANCE_BOOT_TIMEOUT = 10 * 60
SERVICE_INSTANCE_BOOT_DONE_PATTERN = 'Cloud-init .+ finished'