Restoring failed Contrail node
==============================

This guide describes how to replace failed Contrail node in case when Contrail
roles where placed on one node.

After contrail node crash you have to the following steps:

#. Remove failed node from cassandra cluster (on working contrail node)

   .. code-block:: console

    nodetool removenode <ID>, where <ID> is an ID of failed node

#. Deprovision analytics, control, database and config components of failed node
   from contrail db.

   Example:

   .. code-block:: console

    /opt/contrail/utils/provision_config_node.py \
    --api_server_ip 172.21.128.129 \
    --api_server_port 8082 \
    --oper del \
    --host_name node-294.domain.tld \
    --host_ip 172.21.129.193 \
    --admin_user neutron \
    --admin_tenant_name services \
    --admin_password VerySecurePassword!

    /opt/contrail/utils/provision_analytics_node.py \
    --api_server_ip 172.21.128.129 \
    --api_server_port 8082 \
    --oper del \
    --host_name node-294.domain.tld \
    --host_ip 172.21.129.193 \
    --admin_user neutron \
    --admin_tenant_name services \
    --admin_password VerySecurePassword!

    /opt/contrail/utils/provision_control.py \
    --api_server_ip 172.21.128.129 \
    --api_server_port 8082 \
    --oper del \
    --host_name  node-294.domain.tld \
    --host_ip 172.21.129.193 \
    --router_asn 64512 \
    --admin_user neutron \
    --admin_tenant_name services \
    --admin_password VerySecurePassword!

    /opt/contrail/utils/provision_database_node.py \
    --api_server_ip 172.21.128.129 \
    --api_server_port 8082 \
    --oper del \
    --host_name node-294.domain.tld \
    --host_ip 172.21.129.193 \
    --admin_user neutron \
    --admin_tenant_name services \
    --admin_password VerySecurePassword!

#. Add new node with Contrail roles and deploy it by Fuel
