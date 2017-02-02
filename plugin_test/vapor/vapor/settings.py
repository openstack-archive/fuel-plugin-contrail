# Project, contrail and OpenStack settings

import os

import yaml

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

CONTAIL_API_PORT = 8082
CONTAIL_ANALYTICS_PORT = 8081

NEUTRON_CONTRAIL_PLUGIN_CONFIG_PATH = '/etc/neutron/plugins/opencontrail/ContrailPlugin.ini'  # noqa
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
PING_SUCESS_TIMEOUT = 60 * 2

ROLE_CONTRAIL_CONTROLLER = 'contrail-controller'
ROLE_CONTRAIL_ANALYTICS = 'contrail-analytics'
ROLE_CONTRAIL_DB = 'contrail-db'
ROLE_CONTRAIL_COMPUTE = 'contrail-compute'
ROLE_CONTRAIL_CONFIG = 'contrail-config'

CONTRAIL_ROLES_SERVICES_MAPPING = {
    ROLE_CONTRAIL_CONTROLLER: (
        'supervisor-control',
        'contrail-control',
        'contrail-control-nodemgr',
        'contrail-dns',
        'contrail-named',
        'supervisor-config',
        'contrail-api',
        'contrail-config-nodemgr',
        'contrail-device-manager',
        'contrail-discovery',
        'contrail-schema',
        'contrail-svc-monitor',
        'ifmap',
        'supervisor-webui',
        'contrail-webui',
        'contrail-webui-middleware',
        'contrail-database',
        'supervisor-database',
        'contrail-database-nodemgr',
        'kafka',
        'supervisor-support-service', ),
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
        'contrail-vrouter-nodemgr', )
}

CONRTAIL_ROLES_DISTRIBUTION_YAML = os.environ.get(
    'CONRTAIL_ROLES_DISTRIBUTION_YAML',
    os.path.join(
        BASE_DIR, '../roles_distribution_example.yaml'))

with open(CONRTAIL_ROLES_DISTRIBUTION_YAML) as f:
    CONRTAIL_ROLES_DISTRIBUTION = yaml.safe_load(f) or {}

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
        'ifmap',
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

HEAT_TEMPLATES_PATH = os.path.join(BASE_DIR, 'heat')


VROUTER_HEADLESS_MODE_CMD = r"grep -iP '^headless_mode\s*=\s*true' /etc/contrail/contrail-vrouter-agent.conf"  # noqa
