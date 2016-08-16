Restore failed Contrail node
============================

This guide describes how to replace the failed Contrail all-in-one node (with all
Contrail roles assigned) in a multi-node environment.

If your Contrail node has been crashed, follow the steps to fix the issue:

#. Remove failed node from Cassandra cluster (on working contrail node)

   #. Obtain Host-ID of the failed Cassandra node:

      .. code-block:: console

       nodetool status

   #. Remove the failed node:

      .. code-block:: console

       nodetool removenode <Host-ID>

#. Deprovision analytics, control, database, and config components of the failed node
   from contrail db.

   #. Obtain IP address of Contrail API endpoint (Managment VIP):

      .. code-block:: console

         hiera management_vip

      Example of system response:

      .. code-block:: console

         10.109.1.3

   #. Obtain Neutron service password:

      .. code-block:: console

         hiera neutron_config | grep admin_password

      Example of system response:

      .. code-block:: console

         "keystone"=>{"admin_password"=>"VerySecurePassword!"},


   #. Deprovision ``contrail-config``:

      .. code-block:: console

       /opt/contrail/utils/provision_config_node.py \
       --api_server_ip <Managment VIP> \
       --api_server_port 8082 \
       --oper del \
       --host_name node-294.domain.tld \
       --host_ip 172.21.129.193 \
       --admin_user neutron \
       --admin_tenant_name services \
       --admin_password <Neutron password>

   #. Deprovision ``contrail-analytics``:

      .. code-block:: console

       /opt/contrail/utils/provision_analytics_node.py \
       --api_server_ip <Managment VIP> \
       --api_server_port 8082 \
       --oper del \
       --host_name node-294.domain.tld \
       --host_ip 172.21.129.193 \
       --admin_user neutron \
       --admin_tenant_name services \
       --admin_password <Neutron password>

   #. Deprovision ``contrail-control``:

      .. code-block:: console

       /opt/contrail/utils/provision_control.py \
       --api_server_ip <Managment VIP> \
       --api_server_port 8082 \
       --oper del \
       --host_name  node-294.domain.tld \
       --host_ip 172.21.129.193 \
       --router_asn 64512 \
       --admin_user neutron \
       --admin_tenant_name services \
       --admin_password <Neutron password>

   #. Deprovision ``contrail-database``:

      .. code-block:: console

       /opt/contrail/utils/provision_database_node.py \
       --api_server_ip <Managment VIP> \
       --api_server_port 8082 \
       --oper del \
       --host_name node-294.domain.tld \
       --host_ip 172.21.129.193 \
       --admin_user neutron \
       --admin_tenant_name services \
       --admin_password <Neutron password>

#. Add a new node with Contrail roles and deploy it with Fuel
