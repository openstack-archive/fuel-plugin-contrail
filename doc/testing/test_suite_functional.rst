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
    4. Add 3 nodes with "contrail-db", "contarail-config" and "contrail-control" roles on all nodes
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

    1. Create an environment with "Neutron with tunneling segmentation" as a network configuration and CEPH storage
    2. Enable and configure Contrail plugin
    3. Add some controller, compute + storage (at least 4) nodes
    4. Add a node with "contrail-db", "contarail-config" and "contrail-control" roles
    5. Deploy cluster
    6. Run OSTF tests
    7. Delete a compute node and deploy changes
    8. Run OSTF tests
    9. Add a node with "compute" role and deploy changes
    10. Run OSTF tests


Expected results
################

All steps must be completed successfully, without any errors.


Verify HA with deleting Contrail roles
--------------------------------------


ID
##

contrail_ha_with_shutdown_contrail_node


Description
###########

Verify HA with deleting Contrail roles


Complexity
##########

advanced


Steps
#####

    1. Create an environment with "Neutron with tunneling segmentation" as a network configuration
    2. Enable and configure Contrail plugin
    3. Add some controller, compute and storage nodes
    4. Add 4 nodes with "contrail-db", "contarail-config" and "contrail-control" roles
    5. Deploy cluster
    6. Run OSTF tests
    7. Check Controller and Contrail nodes status
    8. Shutdown node with 'contrail-db', "contarail-config" and "contrail-control" roles
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

contrail_add_conrol


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

contrail_delete_conrol


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


Verify that Contrail DB role can be added and deleted after deploying
---------------------------------------------------------------------


ID
##

contrail_add_del_db


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
    10. Delete node with "contrail-db", which was added before
    11. Deploy changes
    12. Run OSTF tests
    13. Check Controller and Contrail nodes status


Expected results
################

All steps must be completed successfully, without any errors.


Deploy Environment with Contrail DB + Ceph multirole
----------------------------------------------------


ID
##

contrail_db_multirole


Description
###########

Deploy Environment with Contrail DB + Ceph multirole


Complexity
##########

Core


Steps
#####

    1. Create an environment with "Neutron with tunneling segmentation" as a network configuration
    2. Enable and configure Contrail plugin
    3. Add some controller, compute nodes
    4. Add 1 node with "contrail-db" + "Ceph-OSD" role, one node with "contrail-control" + "storage-cinder" and 1 node with "contrail-config" + "Ceph-OSD"
    5. Deploy cluster
    6. Run OSTF tests

Expected results
################

All steps must be completed successfully, without any errors.


Deploy Environment with Contrail Control  + Ceph multirole
----------------------------------------------------------


ID
##

contrail_control_multirole


Description
###########

Deploy Environment with Contrail Control  + Ceph multirole


Complexity
##########

Core


Steps
#####

    1. Create an environment with "Neutron with tunneling segmentation" as a network configuration
    2. Enable and configure Contrail plugin
    3. Add some controller, compute + "Ceph-OSD" nodes
    4. Add 1 node with "contrail-control" + "contrail-config" + "Ceph-OSD" multirole and 1 node with "contrail-db" + "storage-cinder"
    5. Deploy cluster
    6. Run OSTF tests

Expected results
################

All steps must be completed successfully, without any errors.


Deploy Environment with Contrail Config + Ceph multirole
--------------------------------------------------------


ID
##

contrail_config_multirole


Description
###########

Deploy Environment with Contrail Config + Ceph multirole


Complexity
##########

Core


Steps
#####

    1. Create an environment with "Neutron with tunneling segmentation" as a network configuration
    2. Enable and configure Contrail plugin
    3. Add some controller, compute + "Ceph-OSD" nodes
    4. Add 1 node with "contrail-config" + "Ceph-OSD" + "storage-cinder" multirole and one node with "contrail-db" + "contrail-control"
    5. Deploy cluster
    6. Run OSTF tests

Expected results
################

All steps must be completed successfully, without any errors.