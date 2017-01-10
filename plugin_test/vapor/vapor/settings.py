# Project, contrail and OpenStack settings

import os

import yaml

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

ROLE_CONTRAIL_CONTROLLER = 'contrail-controller'
ROLE_CONTRAIL_ANALYTICS = 'contrail-analytics'
ROLE_CONTRAIL_DB = 'contrail-db'
ROLE_CONTRAIL_COMPUTE = 'contrail-compute'

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
        'contrail-vrouter-nodemgr')
}


CONRTAIL_ROLES_DISTRIBUTION_YAML = os.environ.get(
    'CONRTAIL_ROLES_DISTRIBUTION_YAML',
    os.path.join(
        os.path.dirname(__file__), '../roles_distribution_example.yaml'))

with open(CONRTAIL_ROLES_DISTRIBUTION_YAML) as f:
    CONRTAIL_ROLES_DISTRIBUTION = yaml.safe_load(f) or {}
