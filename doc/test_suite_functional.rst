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

    1. Log into the Fuel web UI
    2. Press “New OpenStack Environment”
    3. Specify Environment name as test
    4. Set QEMU or KVM as compute
    5. Select 'Neutron with tunneling segmentation' as a network configuration
    6. Set “default” glance and cinder and do not use any Additional Services
    7. Press “Create”
    8. Open the Settings tab of the Fuel web UI
    9. Select the Contrail plugin checkbox and configure plugin settings
    10. Configure network
    11. Add 3 nodes with “contrail-db”, "contarail-config" and "contrail-control" roles on all nodes
    12. Add 2 nodes with “Controller” role and 1 node with “Compute” role and start deploy
    13. Check Controller, Compute and Contrail nodes status and start deploy.
    14. After deploying delete one Controller node and start deploy
    15. After the end of deploy add node with “Controller” role
    16. Run OSTF testsAll steps must be completed successfully, without any errors.


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

    1. Log into the Fuel web UI
    2. Press “New OpenStack Environment”
    3. Specify Environment name as test
    4. Set QEMU or KVM as compute
    5. Select 'Neutron with tunneling segmentation' as a network configuration
    6. Set “default” glance and cinder and do not use any Additional Services
    7. Press “Create”
    8. Open the Settings tab of the Fuel web UI
    9. Select the Contrail plugin checkbox and configure plugin settings
    10. Configure network
    11. Add 3 nodes with “contrail-db”, "contarail-config" and "contrail-control" roles on all nodes
    12. Add 1 nodes with “Controller” role and 2 node with “Compute” role
    13. Check Controller, Compute and Contrail nodes status and start deploy
    14. After deploying delete one Compute node and start deploy
    15. After the end of deploy add node with “Compute” role
    16. Run OSTF testsAll steps must be completed successfully, without any errors.


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

    1. Log into the Fuel web UI
    2. Press “New OpenStack Environment”
    3. Specify Environment name as test
    4. Set QEMU or KVM as compute
    5. Select 'Neutron with tunneling segmentation' as a network configuration
    6. Set “default” glance and cinder. Do not use any Additional Services
    7. Press “Create”
    8. Open the Settings tab of the Fuel web UI
    9. Select the Contrail plugin checkbox and configure plugin settings
    10. Configure network
    11. Add 4 nodes with “contrail-db”, "contarail-config" and "contrail-control" roles on all nodes
    12. Add 3 nodes with “Controller” role and 2 nodes with “Compute” + “Cinder” roles
    13. Start deploy
    14. Check Controller and Contrail nodes status
    15. Remove one node with “contrail-db”, "contarail-config" and "contrail-control" roles
    16. Deploy changes
    17. After the end of deploy run OSTF tests


Expected results
################

All steps must be completed successfully, without any errors.

