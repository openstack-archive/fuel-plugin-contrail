# Project, contrail and OpenStack settings

PATH_TO_CERT = '/tmp/cert.crt'
VERIFY_SSL = False
DISABLE_SSL = True
KEYSTONE_CREDS = {
    'username': 'admin',
    'password': 'secret',
    'tenant_name': 'admin',
}

CONTRAIL_CREDS = {
    'controller_addr': '192.168.1.127'
}

CONTAIL_API_PORT = 8082

NEUTRON_CONTRAIL_PLUGIN_CONFIG_PATH = '/etc/neutron/plugins/opencontrail/ContrailPlugin.ini'  # noqa
