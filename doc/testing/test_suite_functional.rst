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
    3. Add 3 controllers, a compute and a storage nodes
    4. Add a node with "contrail-controller" roles
    5. Add a node with "contrail-analytics" role
    6. Add a node with "contrail-analytics-db" role
    7. Add a node  with "compute-vmware" role
    8. Add 2 nodes  with "contrail-vmware" role
    9. Deploy cluster
    10. Run OSTF tests
    11. Run contrail health check tests
    12. Delete a Controller node and deploy changes
    13. Run OSTF tests
    14. Run contrail health check tests
    15. Add a node with "Controller" role and deploy changes
    16. Run OSTF tests.
    17. Run contrail health check tests

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
    2. Enable and configure Contrail plugin with Vcenter
    3. Add a controller and 3 compute + storage nodes
    4. Add a node with "contrail-analytics" and "contrail-controller" roles
    5. Add a node with "contrail-analytics-db" role
    6. Add a node with "compute-vmware" role
    7. Add 2 nodes with "contrail-vmware" role
    8. Deploy cluster
    9. Run OSTF tests
    10. Run contrail health check tests
    11. Delete a compute node and deploy changes
    12. Run OSTF tests
    13. Add a node with "compute" role and deploy changes
    14. Run OSTF test
    15. Run contrail health check tests


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
    3. Add some controller, compute and storage nodes
    4. Add 3 nodes with "contrail-controller" and "contrail-analytics" roles
    5. Add a node with "contrail-analytics-db" role
    6. Deploy cluster
    7. Run OSTF tests
    8. Check Controller and Contrail nodes status
    9. Shutdown node with "contrail-controller" and "contrail-analytics" roles
    10. Run OSTF tests
    11. Check Controller and Contrail nodes status


Expected results
################

All steps must be completed successfully, without any errors.


Verify that Contrail control role can be added after deploying
--------------------------------------------------------------


ID
##

contrail_add_controller


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
    3. Add a controller and a compute+cinder nodes
    4. Add 2 nodes with "contrail-controller" roles
    5. Add a node with "contrail-analytics" role
    6. Add a node with "contrail-analytics-db" role
    7. Add a node with "compute-vmware" role
    8. Add a node with "contrail-vmware" role
    9. Deploy cluster
    10. Run OSTF tests
    11. Run contrail health check tests
    12. Add one node with "contrail-controller" role
    13. Deploy changes
    14. Run OSTF tests
    15. Run contrail health check tests


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
    4. Add a node with contrail-controller role
    5. Add a node with contrail-analytics and contrail-analytics-db
    6. Deploy cluster and run OSTF tests
    7. Run contrail health check tests
    8. Add node with "compute" role
    9. Deploy changes and run OSTF tests
    10. Run contrail health check tests
    11. Delete node with "compute" role
    12. Deploy cluster and run OSTF tests
    13. Run contrail health check tests


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
       1 contrail-controller
       1 contrail-analytics + contrail-analytics-db
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
    2. Enable and configure Contrail plugin with Vceneter
    3. Add a controller and a compute+cinder nodes
    4. Add a node with "contrail-controller" role
    5. Add a "compute-vmware" node
    6. Add a "contrail-vmware" node
    7. Add a "contrail-analytics-db"+"contrail-analytics" node
    8. Deploy cluster
    9. Run OSTF tests
    10. Run contrail health check tests
    11. Add one node with "contrail-analytics" role
    12. Deploy changes
    13. Run OSTF tests
    14. Run contrail health check tests

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
    3. Add a controller and a compute+cinder nodes
    4. Add a node with "contrail-controller" role
    5. Add a node with "contrail-analytics" and "contrail-analytics-db" roles
    6. Add a node with "contrail-analytics" role
    7. Deploy cluster
    8. Run OSTF tests
    9. Run contrail health check tests
    10. Delete one "contrail-analytics" role
    11. Deploy changes
    12. Run OSTF tests
    13. Run contrail health check tests

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
    4. Add a node with "contrail-controller" role
    5. Add a node with "contrail-analytics-db" and "contrail-analytics" roles
    6. Deploy cluster
    7. Run OSTF tests
    8. Check Controller and Contrail nodes status


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
    3. Add a node with controller and cinder role
    4. Add 2 nodes with compute role
    5. Add 3 nodes with contrail-controller
       and contrail-analytics roles
    6. Add a node with contrail-analytics-db role
    7. Deploy cluster
    8. Run OSTF tests
    9. Run contrail health check tests
    10. Add 2 nodes contrail-analytics-db role
    11. Deploy cluster
    12. Run OSTF tests
    13. Run contrail health check tests


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

    1. Connect to a Fuel with preinstalled Contrail plugin.
    2. Create a new environment with following parameters:
       * Compute: vCenter
       * Networking: Neutron with tunneling segmentation
       * Storage: default
       * Additional services: default
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
       * Contrail-controller
       * Contrail-analytics + contrail-analytics-db
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

    1. Connect to a Fuel with preinstalled Contrail plugin.
    2. Create a new environment with following parameters:
       * Compute: vCenter
       * Networking: Neutron with tunneling segmentation
       * Storage: default
       * Additional services: default
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
       * Contrail-controller + contrail-analytics
       * Contrail-analytics-db
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


ID
##

contrail_private_gateway


Description
###########

Check gateway in private network for single nodegroup deployment


Complexity
##########

Advanced


Steps
#####

    1. Create an environment
    2. Create new netwotk between vSRX ana private network
    3. Enable and configure Contrail plugin
    4. Deploy cluster
    5. Run OSTF tests
    6. Run contrail health check tests


Expected results
################

All steps must be completed successfully, without any errors.
