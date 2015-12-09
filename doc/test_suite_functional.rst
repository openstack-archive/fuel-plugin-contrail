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

    1. Create an environment with "Neutron with tunneling segmentation" as a network configuration and CEPH storage
    2. Enable and configure Contrail plugin
    3. Add some controller (at least 3), compute and storage nodes
    4. Add 3 nodes with "contrail-db", "contarail-config" and "contrail-control" roles on all nodes
    5. Deploy cluster
    6. Run OSTF tests
    7. Delete a Controller node and deploy changes
    8. Run OSTF tests
    9. Add a node with "Controller" role and deploy changes
    10. Run OSTF tests


Expected Results
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

    1. Create an environment with "Neutron with tunneling segmentation" as a network configuration
    2. Enable and configure Contrail plugin
    3. Add some controller, compute (at least 3) and storage nodes
    4. Add a node with "contrail-db", "contarail-config" and "contrail-control" roles
    5. Deploy cluster
    6. Run OSTF tests
    7. Delete a compute node and deploy changes
    8. Run OSTF tests
    9. Add a node with "compute" role and deploy changes
    10. Run OSTF tests


Expected Results
################

All steps must be completed successfully, without any errors.


Verify HA with deleting Contrail roles
---------------------------------------


ID
##

ha_plugin_with_deleting_node


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
    8. Remove one node with 'contrail-db', "contarail-config" and "contrail-control" roles
    9. Deploy changes
    10. Run OSTF tests
    11. Check Controller and Contrail nodes status


Expected results
################

All steps must be completed successfully, without any errors.

