Restoring failed Contrail node
==============================

This guide describes how to replace failed Contrail all-in-one node (with all
contrail roles assigned) in multi-node environment.

After contrail node crash you have to the following steps:

#. Remove failed node from cassandra cluster (on working contrail node)

   #. Obtain Host-ID of failed Cassandra node:

      .. code-block:: console

       nodetool status

   #. Remove node:

      .. code-block:: console

       nodetool removenode <Host-ID>

#. Deprovision analytics, control, database and config components of failed node
   from contrail db.

   #. Obtain Contrail API (Managment VIP) address:

      .. code-block:: console

       # hiera network_metadata | grep vips -A50 | grep management -A1
         "management"=>
          {"ipaddr"=>"10.109.1.3",

   #. Obtain Neutron service password:

      .. code-block:: console

       # hiera neutron_config | grep admin_password
         "keystone"=>{"admin_password"=>"VerySecurePassword!"},


   #. Deprovision contail-config:

      .. code-block:: console

       /opt/contrail/utils/provision_config_node.py \
       --api_server_ip 10.109.1.3 \
       --api_server_port 8082 \
       --oper del \
       --host_name node-294.domain.tld \
       --host_ip 172.21.129.193 \
       --admin_user neutron \
       --admin_tenant_name services \
       --admin_password VerySecurePassword!

   #. Deprovision contail-analytics:

      .. code-block:: console

       /opt/contrail/utils/provision_analytics_node.py \
       --api_server_ip 10.109.1.3 \
       --api_server_port 8082 \
       --oper del \
       --host_name node-294.domain.tld \
       --host_ip 172.21.129.193 \
       --admin_user neutron \
       --admin_tenant_name services \
       --admin_password VerySecurePassword!

   #. Deprovision contail-contol:

      .. code-block:: console

       /opt/contrail/utils/provision_control.py \
       --api_server_ip 10.109.1.3 \
       --api_server_port 8082 \
       --oper del \
       --host_name  node-294.domain.tld \
       --host_ip 172.21.129.193 \
       --router_asn 64512 \
       --admin_user neutron \
       --admin_tenant_name services \
       --admin_password VerySecurePassword!

   #. Deprovision contail-database:

      .. code-block:: console

       /opt/contrail/utils/provision_database_node.py \
       --api_server_ip 10.109.1.3 \
       --api_server_port 8082 \
       --oper del \
       --host_name node-294.domain.tld \
       --host_ip 172.21.129.193 \
       --admin_user neutron \
       --admin_tenant_name services \
       --admin_password VerySecurePassword!

#. Add new node with Contrail roles and deploy it by Fuel
