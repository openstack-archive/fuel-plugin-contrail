===================
Integration testing
===================


Check VM migration on Compute
-----------------------------


ID
##

contrail_vm_migration


Description
###########

Check VM migration on Compute


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
    6. Select "Use Ceph"
    7. Press “Create”
    8. Open the Settings tab of the Fuel web UI and select the Contrail plugin checkbox and configure plugin settings
    9. Verify “Cinder RBD for volumes(Cinder)” in Storage section was selected
    10. Configure network
    11. Add 3 nodes with “contrail-db”, "contarail-config" and "contrail-control" roles on all nodes
    12. Add 1 node with “Controller” role and 2 nodes with “Compute” + “Cinder” role
    13. Start deploy
    14. Log into Openstack Horizon as admin
    15. Launch 2 new instances
    16. In Contrail controller WebUI verify that VMs are present
    17. Migrate one VM in Openstack Horizon with “Live migrate Instance”
    18. In Contrail controller WebUI verify that VM is still present


Expected Results
################

VM should be present after VM migration


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


Deploy Contrail cluster with Ceph on Compute nodes
--------------------------------------------------


ID
##

deploy_contrail_with_base_os_ceph


Description
###########

Deploy Contrail cluster with Ceph on Compute nodes


Complexity
##########

advanced


Steps
#####

    1. Login in Fuel web UI
    2. Press “New OpenStack Environment”
    3. Set Environment Name = ‘test’
    4. Set QEMU or KVM
    5. Select 'Neutron with tunneling segmentation' as a network configuration
    6. Set “default” glance and cinder
    7. Select “Yes, use Ceph” in Storage Backends
    8. Do not use any Additional Services
    9. Press “Create”
    10. Press “Settings” tab
    11. Select the Contrail plugin checkbox and configure plugin settings
    12. Configure network
    13. Add 3 nodes with “contrail-db”, "contarail-config" and "contrail-control" roles on all nodes
    14. Add 1 node with “Controller” role, 1 node with “Compute”  +  ”Storage-Ceph OSD” role and one with ”Storage-Ceph OSD” role
    15. Start deploy
    16. Check nodes status
    17. After the end of deploy run OSTF tests


Expected Results
################

All steps must be completed successfully, without any errors.


Deploy Contrail cluster with Ceilometer
---------------------------------------


ID
##

deploy_contrail_with_ceilometer


Description
###########

Deploy Contrail cluster with Ceilometer


Complexity
##########

advanced


Steps
#####

    1. Login in Fuel web UI
    2. Press “New OpenStack Environment”
    3. Set Environment Name = ‘test’
    4. Set QEMU or KVM
    5. Select 'Neutron with tunneling segmentation' as a network configuration
    6. Set “default” glance and cinder
    7. Select “Install Ceilometer”
    8. Do not use any Additional Services
    9. Press “Create”
    10. Press “Settings” tab
    11. Select the Contrail plugin checkbox and configure plugin settings
    12. Configure network
    13. Add 3 nodes with “contrail-db”, "contarail-config" and "contrail-control" roles on all nodes
    14. Add 1 node with “Controller”+ “Telemetry Mongo DB” role and 1 node with “Compute” role
    15. Start deploy
    16. Check nodes status
    17. After the end of deploy run OSTF tests and pay special attention to the OSTF items which use Ceilometer functionalityAll steps must be completed successfully, without any errors and OSTF run successfully.


Expected Results
################

All steps must be completed successfully, without any errors and OSTF run successfully.


Deploy Contrail cluster with jumbo frames enabled for Private network
---------------------------------------------------------------------


ID
##

contrail_jumbo_frame


Description
###########

Deploy Contrail cluster with jumbo frames enabled for Private network


Complexity
##########

advanced


Steps
#####

    1. Login in Fuel web UI
    2. Press “New OpenStack Environment”
    3. Set Environment Name = ‘test’
    4. Set QEMU or KVM as compute
    5. Select 'Neutron with tunneling segmentation' as a network configuration
    6. Set “default” glance and cinder
    7. Do not use any Additional Services
    8. Press “Create”
    9. Press “Settings” tab
    10. Select the Contrail plugin checkbox and configure plugin settings
    11. Configure network and set mtu 9000 for private network
    12. Add 3 nodes with “contrail-db”, "contarail-config" and "contrail-control" roles on all nodes
    13. Add 1 node with “Controller” role
    14. Enable jumbo MTU on switches with command sudo ip link set dev <fuelnet_name> mtu 9000
    15. Verify it with “ip link” command
    16. Start deploy
    17. Check Controller and Contrail nodes status


Expected Results
################

All steps must be completed successfully, without any errors.


Verify that ‘contrail_control’ role can be deleted and added back to the cluster
--------------------------------------------------------------------------------


ID
##

del_add_contrail_control_node


Description
###########

Verify that ‘contrail_control’ role can be deleted and added back to the cluster


Complexity
##########

advanced


Steps
#####

    1. Login in Fuel web UI
    2. Press “New OpenStack Environment”
    3. Set Environment Name = ‘test’
    4. Set QEMU or KVM as compute
    5. Select 'Neutron with tunneling segmentation' as a network configuration
    6. Set “default” glance and cinder
    7. Do not use any Additional Services
    8. Press “Create”
    9. Press “Settings” tab
    10. Select the Contrail plugin checkbox and configure plugin settings
    11. Configure network
    12. Add 3 nodes with “contrail-db”, "contarail-config" and "contrail-control" roles on seperate nodes
    13. Add 1 node with “Controller” role
    14. Add 1 node with “Compute” role
    15. Start deploy
    16. Check Controller and Contrail nodes status
    17. Delete ‘contrail_control’ role
    18. Deploy changes
    19. Add ‘contrail_control’ role
    20. Deploy changes
    21. After the end of deploy run OSTF tests


Expected Results
################

All steps must be completed successfully, without any errors.


Verify that ‘contrail_config’ role can be deleted and added back to the cluster
-------------------------------------------------------------------------------


ID
##

del_add_contrail_config_node


Description
###########

Verify that ‘contrail_config’ role can be deleted and added back to the cluster

 
Complexity
##########

advanced


Steps
#####

    1. Login in Fuel web UI
    2. Press “New OpenStack Environment”
    3. Set Environment Name = ‘test’
    4. Set QEMU or KVM as compute
    5. Select 'Neutron with tunneling segmentation' as a network configuration
    6. Set “default” glance and cinder
    7. Do not use any Additional Services
    8. Press “Create”
    9. Press “Settings” tab
    10. Select the Contrail plugin checkbox and configure plugin settings
    11. Configure network
    12. Add 3 nodes with “contrail-db”, "contarail-config" and "contrail-control" roles on seperate nodes
    13. Add 1 node with “Controller” role
    14. Add 1 node with “Compute” role
    15. Start deploy
    16. Check Controller and Contrail nodes status
    17. Delete ‘contrail_config’ role
    18. Deploy changes
    19. Add ‘contrail_config’ role
    20. Deploy changes
    21. After the end of deploy run OSTF tests


Expected Results
################

All steps must be completed successfully, without any errors.


Deploy ‘contrail_db’ on one node and ‘contrail_config’, ‘contrail_control’ on other node
----------------------------------------------------------------------------------------


ID
##

deploy_contrail_db_seperatly


Description
###########

Verify deploy ‘contrail_db’ on one node and ‘contrail_config’, ‘contrail_control’ on other node


Complexity
##########

advanced


Steps
#####

    1. Login in Fuel web UI
    2. Press “New OpenStack Environment”
    3. Set Environment Name = ‘test’
    4. Set QEMU or KVM as compute
    5. Select 'Neutron with tunneling segmentation' as a network configuration
    6. Set “default” glance and cinder
    7. Do not use any Additional Services
    8. Press “Create”
    9. Press “Settings” tab
    10. Select the Contrail plugin checkbox and configure plugin settings
    11. Configure network
    12. Add 1 node with “contrail-db” and "contarail-config" + "contrail-control" roles on the second node
    13. Add 1 node with “Controller” role
    14. Add 1 node with “Compute” role
    15. Start deploy
    16. Check Controller and Contrail nodes status
    17. After the end of deploy run OSTF tests


Expected Results
################

All steps must be completed successfully, without any errors.


Deploy ‘contrail_db’, ‘contrail_config’ on one node and ‘contrail_control’ on other node
----------------------------------------------------------------------------------------


ID
##

deploy_contrail_control_seperatly


Description
###########

Verify deploy ‘contrail_db’, ‘contrail_config’ on one node and ‘contrail_control’ on other node


Complexity
##########

advanced


Steps
#####

    1. Login in Fuel web UI
    2. Press “New OpenStack Environment”
    3. Set Environment Name = ‘test’
    4. Set QEMU or KVM as compute
    5. Select 'Neutron with tunneling segmentation' as a network configuration
    6. Set “default” glance and cinder
    7. Do not use any Additional Services
    8. Press “Create”
    9. Press “Settings” tab
    10. Select the Contrail plugin checkbox and configure plugin settings
    11. Configure network
    12. Add 1 node with ‘contrail-db‘ + ‘contrail_config’ and 1 node with ‘contrail_control’ roles
    13. Add 1 node with “Controller” role
    14. Add 1 node with “Compute” role
    15. Start deploy
    16. After the end of deploy run OSTF tests


Expected Results
################

All steps must be completed successfully, without any errors.


Deploy ‘contrail_config’ on one node and  ‘contrail_db’, ‘contrail_control’ on other node
-----------------------------------------------------------------------------------------


ID
##

del_add_contrail_config_node


Description
###########

Verify deploy ‘contrail_config’ on one node and  ‘contrail_db’, ‘contrail_control’ on other node

Complexity
##########

advanced


Steps
#####

    1. Login in Fuel web UI
    2. Press “New OpenStack Environment”
    3. Set Environment Name = ‘test’ 
    4. Set QEMU or KVM as compute
    5. Select 'Neutron with tunneling segmentation' as a network configuration 
    6. Set “default” glance and cinder
    7. Do not use any Additional Services
    8. Press “Create”
    9. Press “Settings” tab
    10. Select the Contrail plugin checkbox and configure plugin settings
    11. Configure network 
    12. Add 1 node with ‘contrail-db‘ + ‘contrail_control’ and 1 node with ‘contrail_config’ roles
    13. Add 1 node with “Controller” role
    14. Add 1 node with “Compute” role
    15. Start deploy
    16. After the end of deploy run OSTF tests


Expected Results
################
    
All steps must be completed successfully, without any errors.

