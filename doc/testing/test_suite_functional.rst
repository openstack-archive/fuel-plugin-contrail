==================
Functional testing
==================


Check that Controller node can be deleted and added again
---------------------------------------------------------


ID
##

contrail_plugin_add_delete_controller_node


Description
###########

Verify that Controller node can be deleted and added after deploying


Complexity
##########

advanced


Steps
#####

    1. Create an environment
    2. Enable and configure Contrail plugin with Vcenter
    3. Enable dedicated analytics DB
    4. Add 3 controllers, a compute and a storage nodes
    5. Add 3 nodes with "contrail-db", "contrail-config",
       "contrail-analytics" and "contrail-control" roles on all nodes
    6. Add a node with "contrail-analytics-db" role
    7. Add a node  with "compute-vmware" role
    8. Add a node  with "contrail-vmware" role
    9. Deploy cluster
    10. Run OSTF tests
    11. Delete a Controller node and deploy changes
    12. Run OSTF tests
    13. Add a node with "Controller" role and deploy changes
    14. Run OSTF tests. All steps must be completed successfully,
        without any errors.


Expected results
################

All steps must be completed successfully, without any errors.


Check that Compute node can be deleted and added again
------------------------------------------------------


ID
##

contrail_plugin_add_delete_compute_node


Description
###########

Verify that Compute node can be deleted and added after deploying


Complexity
##########

advanced


Steps
#####

    1. Create an environment
    2. Enable and configure Contrail plugin
    3. Enable dedicated analytics DB
    4. Add a controller and 3 compute + storage nodes
    5. Add a node with "contrail-db", "contarail-config",
       "contrail-analytics" and "contrail-control" roles
    6. Add a node with "contrail-analytics-db" role
    7. Deploy cluster
    8. Run OSTF tests
    9. Delete a compute node and deploy changes
    10. Run OSTF tests
    11. Add a node with "compute" role and deploy changes
    12. Run OSTF test


Expected results
################

All steps must be completed successfully, without any errors.


Verify HA with shutdown Contrail roles
--------------------------------------


ID
##

contrail_ha_with_shutdown_contrail_node


Description
###########

Verify HA with shutdown Contrail roles


Complexity
##########

advanced


Steps
#####

    1. Create an environment
    2. Enable and configure Contrail plugin
    3. Enable dedicated analytics DB
    4. Add some controller, compute and storage nodes
    5. Add 3 nodes with "contrail-db", "contarail-config"
       "contrail-analytics",
       and "contrail-control" roles
    6. Add a node with "contrail-analytics-db" role
    7. Deploy cluster
    8. Run OSTF tests
    9. Check Controller and Contrail nodes status
    10. Shutdown node with 'contrail-db', "contarail-config" and
       "contrail-control" roles
    11. Run OSTF tests
    12. Check Controller and Contrail nodes status


Expected results
################

All steps must be completed successfully, without any errors.


Verify that Contrail control role can be added after deploying
--------------------------------------------------------------


ID
##

contrail_add_control


Description
###########

Verify that Contrail control role can be added after deploying


Complexity
##########

Core


Steps
#####

    1. Create an environment with "Neutron with tunneling segmentation"
       as a network configuration
    2. Enable and configure Contrail plugin with Vcenter
    3. Enable dedicated analytics DB
    4. Add a controller and a compute+cinder nodes
    5. Add a node with "contrail-control",
       and "contrail-db" roles
    6. Add a node with "contrail-config" and "contrail-analytics" roles
    7. Add a node with "contrail-analytics-db" role
    8. Add a node with "compute-vmware" role
    9. Add a node with "contrail-vmware" role
    10. Deploy cluster
    11. Run OSTF tests
    12. Add one node with "contrail-control" role
    13. Deploy changes
    14. Run OSTF tests


Expected results
################

All steps must be completed successfully, without any errors.


Verify that Contrail config role can be added after deploying
-------------------------------------------------------------


ID
##

contrail_add_config


Description
###########

Verify that Contrail config role can be added after deploying


Complexity
##########

Core


Steps
#####

    1. Create an environment with "Neutron with tunneling segmentation"
       as a network configuration
    2. Enable and configure Contrail plugin
    3. Enable dedicated analytics DB
    4. Add a controller and a compute+cinder nodes
    5. Add a node with "contrail-config" and "contrail-db" roles
    6. Add a "contrail-control"+"contrail-analytics"
       +"contrail-analytics-db" node
    7. Add a "contrail-analytics-db" node
    8. Deploy cluster
    9. Run OSTF tests
    10. Add one node with "contrail-config" role
    11. Deploy changes
    12. Run OSTF tests


Expected results
################

All steps must be completed successfully, without any errors.


Verify that Contrail control role can be deleted after deploying
----------------------------------------------------------------


ID
##

contrail_delete_control


Description
###########

Verify that Contrail control role can be deleted after deploying


Complexity
##########

Core


Steps
#####

    1. Create an environment with "Neutron with tunneling segmentation"
       as a network configuration
    2. Enable and configure Contrail plugin
    3. Enable dedicated analytics DB
    4. Add a controller and a compute+cinder nodes
    5. Add a node with 'contrail-control'+'contrail-config'
       +'contrail-db' roles
    6. Add a node with 'contrail-analytics'+'contrail-analytics-db'
      roles
    7. Add a node with "contrail-control" role
    8. Deploy cluster
    9. Run OSTF tests
    10. Delete one "contrail-control" role
    11. Deploy changes
    12. Run OSTF tests


Expected results
################

All steps must be completed successfully, without any errors.


Verify that Contrail config role can be deleted after deploying
---------------------------------------------------------------


ID
##

contrail_delete_config


Description
###########

Verify that Contrail config role can be deleted after deploying


Complexity
##########

Core


Steps
#####

    1. Create an environment with "Neutron with tunneling segmentation"
       as a network configuration
    2. Enable and configure Contrail plugin
    3. Enable dedicated analytics DB
    4. Add a controller and a compute+cinder nodes
    5. Add a node with all compatible contrail roles
    6.Add a node with "contrail-config" role
    7. Add a node with "contrail-analytics-db" role
    8. Deploy cluster
    9. Run OSTF tests
    10. Delete one "contrail-config" role
    11. Deploy changes
    12. Run OSTF tests


Expected results
################

All steps must be completed successfully, without any errors.


Verify that Contrail DB role can be added after deploying
---------------------------------------------------------


ID
##

contrail_add_db


Description
###########

Verify that Contrail DB role can be added and deleted after deploying


Complexity
##########

Core


Steps
#####

    1. Create an environment with "Neutron with tunneling segmentation"
       as a network configuration
    2. Enable and configure Contrail plugin
    3. Enable dedicated analytics DB
    4. Add a controller and a compute+cinder nodes
    5. Add a node with all compatible contrail roles
    6. Add a node with 'contrail-analytics-db' role
    7. Deploy cluster
    8. Add one node with "contrail-db" role
    9. Deploy changes
    10. Run OSTF tests


Expected results
################

All steps must be completed successfully, without any errors.


Check that a Compute node can be deleted and added again with CephOSD
---------------------------------------------------------------------


ID
##

contrail_add_delete_compute_ceph


Description
###########

Verify that Compute node can be deleted and added after deploying with CephOSD as a storage backend


Complexity
##########

advanced


Steps
#####

    1. Create an environment with "Neutron with tunneling segmentation" as a network configuration
    2. Enable and configure Contrail plugin
    3. Add a node with "controller" + "mongo" roles and  3 nodes with "compute" + "ceph-osd" roles
    4. Add a node with all contrail roles
    5. Deploy cluster and run OSTF tests
    6. Check Controller and Contrail nodes status
    7. Add node with "compute" role
    8. Deploy changes and run OSTF tests
    9. Delete node with "compute" role
    10. Deploy changes
    11. Run OSTF tests


Expected results
################

All steps must be completed successfully, without any errors.


Check configured no default contrail parameters via Contrail WEB.
-----------------------------------------------------------------


ID
##

contrail_no_default


Description
###########

Verify that all configured contrail parameters present in the Contrail WEB.


Complexity
##########

Core


Steps
#####

    1. Install contrail plugin.
    2. Create cluster.
    3. Set following no defaults contrail parameters:
       * contrail_api_port
       * contrail_route_target
       * contrail_gateways
       * contrail_external
       * contrail_asnum
    4. Add nodes:
       1 all contrail-specified roles
       1 controller
       1 compute
    5. Deploy cluster.
    6. Verify that all configured contrail parameters present in
       the Contrail WEB.


Expected results
################

All steps must be completed successfully, without any errors.


Verify that Contrail analytics role can be added after deploying
----------------------------------------------------------------


ID
##

contrail_add_analytics


Description
###########

Verify that Contrail analytics role can be added after deploying


Complexity
##########

Core


Steps
#####

    1. Create an environment with "Neutron with tunneling segmentation"
       as a network configuration
    2. Enable and configure Contrail plugin
    3. Enable dedicated analytics DB
    4. Add a controller and a compute+cinder nodes
    5. Add a node with "contrail-config" and "contrail-control" roles
    6. Add a "contrail-db"  node
    7. Add a "contrail-analytics-db"+"contrail-analytics" node
    8. Deploy cluster
    9. Run OSTF tests
    10. Add one node with "contrail-analytics" role
    11. Deploy changes
    12. Run OSTF tests


Expected results
################

All steps must be completed successfully, without any errors.


Verify that Contrail analytics role can be deleted after deploying
------------------------------------------------------------------


ID
##

contrail_delete_analytics


Description
###########

Verify that Contrail analytics role can be deleted after deploying


Complexity
##########

Core


Steps
#####

    1. Create an environment with "Neutron with tunneling segmentation"
       as a network configuration
    2. Enable and configure Contrail plugin
    3. Enable dedicated analytics DB
    4. Add a controller and a compute+cinder nodes
    5. Add a node with all compatible contrail roles
    6. Add a node with 'contrail-analytics-db' roles
    7. Add a node with "contrail-analytics" role
    8. Deploy cluster
    9. Run OSTF tests
    10. Delete one "contrail-analytics" role
    11. Deploy changes
    12. Run OSTF tests

Expected results
################

All steps must be completed successfully, without any errors.


Verify that node with all Contrail roles can be added after deploying
---------------------------------------------------------------------


ID
##

contrail_add_all_contrail


Description
###########

Verify that after deploying can be added an all contrail roles node

Complexity
##########

Core


Steps
#####

    1. Create an environment with "Neutron with tunneling segmentation"
       as a network configuration and Ceph-OSD storage
    2. Enable and configure Contrail plugin with Vcenter
    3. Enable dedicated analytics DB
    4. Add 3 nodes with "controller" + "ceph-osd" roles
    5. Add 2 nodes with "compute" + "ceph-osd" roles
    6. Add a node with 'contrail-control'+'contrail-config'+
       'contrail-db' roles
    7. Add a node with 'contrail-analytics'+'contrail-analytics-db'
       roles
    8. Add compute-vmware node
    9. Add contrail-vmware node
    10. Deploy cluster and run OSTF tests
    11. Add a node with all compatible contrail roles
    12. Deploy changes and run OSTF tests


Expected results
################

All steps must be completed successfully, without any errors.


Verify that we can disable OSTF networks provisioning
-----------------------------------------------------


ID
##

contrail_ostf_net_provisioning_disable


Description
###########

Verify that we can deploy environment with disabled OSTF networks provisioning


Complexity
##########

Core


Steps
#####

    1. Create an environment with "Neutron with tunneling segmentation" as a network configuration
    2. Enable and configure Contrail plugin without OSTF network provisioning
    3. Add some controller, compute and cinder nodes
    4. Add a node with "contrail-config" and "contrail-control" roles
    5. Add a node with "contrail-db" and "contrail-analytics" roles
    6. Deploy cluster
    7. Run OSTF tests
    8. Check Controller and Contrail nodes status


Expected results
################

All steps must be completed successfully, without any errors.


Verify that Analytics DB node can be added after deploying
----------------------------------------------------------


ID
##

contrail_add_analytics_db


Description
###########

Verify that Analytics DB node can be added after deploying


Complexity
##########

Core


Steps
#####

    1. Create an environment
    2. Enable and configure Contrail plugin
    3. Add 3 nodes with "controller" + "ceph-osd" roles
    4. Add 2 nodes with "compute" + "cinder" roles
    5. Add a node with contrail-config, contrail-control
       and contrail-db roles
    6. Add a node with contrail-analytics role
    7. Deploy cluster
    8. Run OSTF tests
    9. Run contrail health check tests
    10. Enable dedicated analytics DB
    11. Add a node with contrail-analytics-db role
    12. Deploy cluster
    13. Run OSTF tests
    14. Run contrail health check tests


Expected results
################

All steps must be completed successfully, without any errors.


Verify that two Analytics DB nodes can be added to exist Analytics DB
---------------------------------------------------------------------


ID
##

contrail_add_ha_analytics_db


Description
###########

Verify that two Analytics DB nodes can be added to exist Analytics DB


Complexity
##########

Core


Steps
#####

    1. Create an environment
    2. Enable and configure Contrail plugin
    3. Enable dedicated analytics DB
    4. Add a node with controller and cinder role
    5. Add 2 nodes with compute role
    6. Add 3 nodes with contrail-config, contrail-control,
       contrail-db and contrail-analytics roles
    7. Add a node with contrail-analytics-db role
    8. Deploy cluster
    9. Run OSTF tests
    10. Run contrail health check tests
    11. Add 2 nodes contrail-analytics-db role
    12. Deploy cluster
    13. Run OSTF tests
    14. Run contrail health check tests


Expected results
################

All steps must be completed successfully, without any errors.


Contrail VMWare add contrail_vmware
-----------------------------------


ID
##

contrail_vmware_add_contrail_vmware


Description
###########

Verify that Contrail-vmware role can be added after deploying


Complexity
##########

advanced


Steps
#####

    1. Create an environment with "Neutron with tunneling
       segmentation" as a network configuration
    3. Run script that prepares vmware part for deployment (creates few Distributed
       Switches and spawns virtual machine on each ESXi node)
    4. Configure Contrail plugin settings:
       * Datastore name
       * Datacenter name
       * Uplink for DVS external
       * Uplink for DVS private
       * DVS external
       * DVS internal
       * DVS private
    5. Configure Openstack settings:
       * Set VMWare vCenter/ESXi datastore for images (Glance)VMWare
         vCenter/ESXi datastore for images (Glance).
    6. Configure VMware vCenter settings on VMware tab.
    7. Deploy cluster with following node configuration:
       * Controller
       * Compute
       * ComputeVMWare
       * Contrail-config + contrail-db + contrail-control + contrail-analytics
       * Contrail-vmware
    8. Run OSTF tests
    9. Add new ESXI host.
    10. Run script that prepares vmware part for deployment
    11. Add one node with contrail-vmware role
    12. Deploy changes
    13. Run OSTF tests
    14. Run contrail health check tests


Expected results
################

All steps should pass


Contrail VMWare delete contrail_vmware
--------------------------------------


ID
##

contrail_vmware_delete_contrail_vmware


Description
###########

Verify that Contrail-vmware role can be deleted after deploying


Complexity
##########

advanced


Steps
#####

    1. Create an environment with "Neutron with tunneling
       segmentation" as a network configuration
    3. Run script that prepares vmware part for deployment (creates few Distributed
       Switches and spawns virtual machine on each ESXi node)
    4. Configure Contrail plugin settings:
       * Datastore name
       * Datacenter name
       * Uplink for DVS external
       * Uplink for DVS private
       * DVS external
       * DVS internal
       * DVS private
    5. Configure VMware vCenter settings on VMware tab.
    6. Deploy cluster with following node configuration:
       * Controller
       * Compute
       * ComputeVMWare
       * Contrail-config + contrail-db + contrail-control + contrail-analytics
       * Contrail-vmware
       * Contrail-vmware
    7. Run OSTF tests
    8. Remove one ESXI host.
    9. Run script that prepares vmware part for deployment
    10. Add one node with contrail-vmware role
    11. Deploy changes
    12. Run OSTF tests
    13. Run contrail health check tests


Expected results
################

All steps should pass
