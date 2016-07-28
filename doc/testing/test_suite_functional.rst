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
    3. Add some controller and compute+cinder nodes
    4. Add a node with "contrail-control" and "contrail-db" roles
    5. Add a node with "contrail-config" and "contrail-analytics" roles
    6. Deploy cluster
    7. Run OSTF tests
    8. Check Controller and Contrail nodes status
    9. Add a node with "contrail-control" role
    10. Deploy changes
    11. Run OSTF tests
    12. Check Controller and Contrail nodes status


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
    3. Add some controller, compute and cinder nodes
    4. Add a node with "contrail-config" and "contrail-db" roles
    5. Add a node with "contrail-control" and "contrail-analytics" roles
    6. Deploy cluster
    7. Run OSTF tests
    8. Check Controller and Contrail nodes status
    9. Add a node with "contrail-config" role
    10. Deploy changes
    11. Run OSTF tests
    12. Check Controller and Contrail nodes status


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
    3. Add some controller, compute and cinder nodes
    4. Add a node with all contrail roles
    5. Add a node with "contrail-control" role
    6. Deploy cluster
    7. Run OSTF tests
    8. Check Controller and Contrail nodes status
    9. Delete the "contrail-control" role
    10. Deploy changes
    11. Run OSTF tests
    12. Check Controller and Contrail nodes status


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
    3. Add some controller, compute and cinder nodes
    4. Add a node with all contrail roles
    5. Add a node with "contrail-config" role
    6. Deploy cluster
    7. Run OSTF tests
    8. Check Controller and Contrail nodes status
    9. Remove the node with "contrail-config" role
    10. Deploy changes
    11. Run OSTF tests
    12. Check Controller and Contrail nodes status


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
    3. Add some controller, compute and cinder nodes
    4. Add a node with all contrail roles
    5. Deploy cluster
    6. Check Controller and Contrail nodes status
    7. Add a node with "contrail-db" role
    8. Deploy changes
    9. Run OSTF tests


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

    1. Create an environment with "Neutron with tunneling segmentation" as a network configuration
    2. Enable and configure Contrail plugin
    3. Add some controller, compute and cinder nodes
    4. Add a node with "contrail-config" and "contrail-control" roles
    5. Add a node with "contrail-db" and "contrail-analytics" roles
    6. Deploy cluster
    7. Run OSTF tests
    8. Check Controller and Contrail nodes status
    9. Add a node with "contrail-analytics" role
    10. Deploy changes
    11. Run OSTF tests
    12. Check Controller and Contrail nodes status


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

    1. Create an environment with "Neutron with tunneling segmentation" as a network configuration
    2. Enable and configure Contrail plugin
    3. Add some controller, compute and cinder nodes
    4. Add a node with all contrail roles
    5. Add a node with "contrail-analytics" role
    6. Deploy cluster
    7. Run OSTF tests
    8. Check Controller and Contrail nodes status
    9. Delete the "contrail-analytics" node
    10. Deploy changes
    11. Run OSTF tests
    12. Check Controller and Contrail nodes status


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

    1. Create an environment with "Neutron with tunneling segmentation" as a network configuration and Ceph-OSD storage
    2. Enable and configure Contrail plugin
    3. Add some controller, compute and Ceph-OSD nodes
    4. Add a node with all contrail roles
    5. Deploy cluster
    6. Run OSTF tests
    7. Check Controller and Contrail nodes status
    8. Add a node with all contrail roles
    9. Deploy changes
    10. Run OSTF tests
    11. Check Controller and Contrail nodes status


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
