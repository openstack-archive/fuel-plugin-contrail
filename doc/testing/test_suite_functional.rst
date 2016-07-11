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

    1. Create an environment with "Neutron with tunneling segmentation" as a network configuration
    2. Enable and configure Contrail plugin
    3. Add some controller (at least 3), compute and storage nodes
    4. Add 3 nodes with "contrail-db", "contrail-config", "contrail-analytics" and "contrail-control" roles on all nodes
    5. Deploy cluster
    6. Run OSTF tests
    7. Delete a Controller node and deploy changes
    8. Run OSTF tests
    9. Add a node with "Controller" role and deploy changes
    10. Run OSTF tests


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

    1. Create an environment with "Neutron with tunneling segmentation" as a network configuration and Cinder storage
    2. Enable and configure Contrail plugin
    3. Add some controller, compute + storage nodes
    4. Add a node with "contrail-db", "contarail-config", "contrail-analytics"  and "contrail-control" roles
    5. Deploy cluster
    6. Run OSTF tests
    7. Delete a compute node and deploy changes
    8. Run OSTF tests
    9. Add a node with "compute" role and deploy changes
    10. Run OSTF tests


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

    1. Create an environment with "Neutron with tunneling segmentation" as a network configuration
    2. Enable and configure Contrail plugin
    3. Add some controller, compute and storage nodes
    4. Add 3 nodes with "contrail-db", "contarail-config", "contrail-analytics" and "contrail-control" roles
    5. Deploy cluster
    6. Run OSTF tests
    7. Check Controller and Contrail nodes status
    8. Shutdown a node with "contrail-db", "contarail-config", "contrail-analytics" and "contrail-control" roles
    9. Deploy changes
    10. Run OSTF tests
    11. Check Controller and Contrail nodes status


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

    1. Create an environment with "Neutron with tunneling segmentation" as a network configuration
    2. Enable and configure Contrail plugin
    3. Add some controller, compute nodes
    4. Add 1 node with "contrail-control", "contrail-config" and "contrail-db" roles
    5. Deploy cluster
    6. Run OSTF tests
    7. Check Controller and Contrail nodes status
    8. Add one node with "contrail-control" role
    9. Deploy changes
    10. Run OSTF tests
    11. Check Controller and Contrail nodes status


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

    1. Create an environment with "Neutron with tunneling segmentation" as a network configuration
    2. Enable and configure Contrail plugin
    3. Add some controller, compute nodes
    4. Add 1 node with "contrail-control", "contrail-db", "contrail-config" roles
    5. Deploy cluster
    6. Run OSTF tests
    7. Check Controller and Contrail nodes status
    8. Add one node with "contrail-config" role
    9. Deploy changes
    10. Run OSTF tests
    11. Check Controller and Contrail nodes status


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

    1. Create an environment with "Neutron with tunneling segmentation" as a network configuration
    2. Enable and configure Contrail plugin
    3. Add some controller, compute nodes
    4. Add 1 node with "contrail-control", "contrail-config" and "contrail-db" roles and 1 node with "contrail-control" role
    5. Deploy cluster
    6. Run OSTF tests
    7. Check Controller and Contrail nodes status
    8. Delete one "contrail-control" role
    9. Deploy changes
    10. Run OSTF tests
    11. Check Controller and Contrail nodes status


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

    1. Create an environment with "Neutron with tunneling segmentation" as a network configuration
    2. Enable and configure Contrail plugin
    3. Add some controller, compute nodes
    4. Add 1 node with "contrail-control", "contrail-config" and 1 node with "contrail-config", "contrail-db" and 1 node with "contrail-config" roles
    5. Deploy cluster
    6. Run OSTF tests
    7. Check Controller and Contrail nodes status
    8. Remove one node with "contrail-config" role
    9. Deploy changes
    10. Run OSTF tests
    11. Check Controller and Contrail nodes status


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

    1. Create an environment with "Neutron with tunneling segmentation" as a network configuration
    2. Enable and configure Contrail plugin
    3. Add some controller, compute nodes
    4. Add 1 node with "contrail-control", "contrail-config" and "contrail-db" roles
    5. Deploy cluster
    6. Check Controller and Contrail nodes status
    7. Add one node with "contrail-db" role
    8. Deploy changes
    9. Run OSTF tests


Expected results
################

All steps must be completed successfully, without any errors.


Uninstall of plugin
-------------------


ID
##

uninstall_contrail_plugin


Description
###########

Uninstall of plugin


Complexity
##########

Core


Steps
#####

    1. Remove plugin: fuel plugins --remove <fuel-plugin-name>==<fuel-plugin-version>
    2. Check that it was removed successfully: fuel plugins


Expected results
################

Contrail plugin was removed successfully


Check that a Compute node can be deleted and added again with CephOSD
---------------------------------------------------------------------


ID
##

contrail_plugin_add_delete_compute_ceph


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
    4. Add node with "contrail-control", "contrail-config" and "contrail-db" roles
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
       1 contrail-config+contrail-control+contrail-db
       1 controller
       1 compute
    5. Deploy cluster.
    6. Verify that all configured contrail parameters present in
       the Contrail WEB.


Expected results
################

All steps must be completed successfully, without any errors.
