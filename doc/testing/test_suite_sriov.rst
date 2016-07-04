=====
SRIOV
=====


Contrail HA SRIOV
-----------------


ID
##

contrail_ha_sriov


Description
###########

Check Contrail deploy HA + SRIOV


Complexity
##########

advanced


Steps
#####

    1. Create an environment with "Neutron with tunneling segmentation" as a network configuration
    2. Enable and configure Contrail plugin
    3. Deploy cluster with some controller, compute+cinder, compute+sriov and contrail-specified nodes
    4. Run OSTF tests


Expected results
################

All steps must be completed successfully, without any errors.


Contrail SRIOV add compute
--------------------------


ID
##

contrail_sriov_add_compute


Description
###########

Check Contrail deploy SRIOV add compute


Complexity
##########

advanced


Steps
#####

    1. Create an environment with "Neutron with tunneling segmentation" as a network configuration and CEPH storage
    2. Enable and configure Contrail plugin
    3. Deploy cluster with some controller, compute+cinder, compute+sriov and contrail-specified nodes
    4. Run OSTF tests
    5. Add a node with compute roles
    6. Deploy changes
    7. Run OSTF tests


Expected results
################

All steps must be completed successfully, without any errors.


Contrail SRIOV delete compute
-----------------------------


ID
##

contrail_sriov_delete_compute


Description
###########

Check Contrail deploy SRIOV delete compute


Complexity
##########

advanced


Steps
#####

    1. Create an environment with "Neutron with tunneling segmentation" as a network configuration and Cinder storage
    2. Enable and configure Contrail plugin
    3. Deploy cluster with some controller, compute+cinder, compute+sriov and contrail-specified nodes
    4. Run OSTF tests
    5. Delete a node with compute role
    6. Deploy changes
    7. Run OSTF tests


Expected results
################

All steps must be completed successfully, without any errors.



Contrail SRIOV add SRIOV
------------------------


ID
##

contrail_sriov_add_sriov


Description
###########

Check Contrail deploy SRIOV add SRIOV


Complexity
##########

advanced


Steps
#####

    1. Create an environment with "Neutron with tunneling segmentation" as a network configuration and CEPH storage
    2. Enable and configure Contrail plugin
    3. Deploy cluster with some controller, compute+cinder, compute+sriov and contrail-specified nodes
    4. Run OSTF tests
    5. Add a node with compute+sriov role
    6. Deploy changes
    7. Run OSTF tests


Expected results
################

All steps must be completed successfully, without any errors.


Contrail SRIOV delete SRIOV
---------------------------


ID
##

contrail_sriov_delete_sriov


Description
###########

Check Contrail deploy SRIOV delete SRIOV


Complexity
##########

advanced


Steps
#####

    1. Create an environment with "Neutron with tunneling segmentation" as a network configuration and CEPH storage
    2. Enable and configure Contrail plugin
    3. Deploy cluster with some controller, compute+cinder, compute+sriov and contrail-specified nodes
    4. Run OSTF tests
    5. Delete a node with compute+sriov roles
    6. Deploy changes
    7. Run OSTF tests


Expected results
################

All steps must be completed successfully, without any errors.


Check updating core repos with Contrail plugin and SRIOV
--------------------------------------------------------


ID
##

contrail_sriov_update_core_repos


Description
###########

Check updating core repos with Contrail plugin and SRIOV


Complexity
##########

advanced


Steps
#####

    1. Deploy cluster with some controller, compute+cinder, compute+sriov and contrail-specified nodes
    2. Run “fuel-createmirror -M” on the master node
    3. Update repos for all deployed nodes with command "fuel --env <ENV_ID> node --node-id <NODE_ID1>, <NODE_ID2>, <NODE_ID_N> --tasks upload_core_repos" on the master node


Expected results
################

All steps must be completed successfully, without any errors


Contrail SRIOV add controller
-----------------------------


ID
##

contrail_sriov_add_controller


Description
###########

Verify that controller node can be added after deploy


Complexity
##########

advanced


Steps
#####

    1. Create an environment with "Neutron with tunneling segmentation" as a network configuration and CEPH storage
    2. Enable and configure Contrail plugin
    3. Deploy cluster with some controller, compute+cinder, compute+sriov and contrail-specified nodes
    4. Run OSTF tests
    5. Add a node with "controller" role
    6. Deploy changes
    7. Run OSTF tests


Expected results
################

All steps must be completed successfully, without any errors


Contrail SRIOV delete controller
--------------------------------


ID
##

contrail_sriov_delete_controller


Description
###########

Verify that controller node can be added and deleted after deploy


Complexity
##########

advanced


Steps
#####

    1. Create an environment with "Neutron with tunneling segmentation" as a network configuration and CEPH storage
    2. Enable and configure Contrail plugin
    3. Deploy cluster with some controller, compute+cinder, compute+sriov and contrail-specified nodes
    4. Run OSTF tests
    5. Delete a node with "controller" role
    6. Deploy changes
    7. Run OSTF tests


Expected results
################

All steps must be completed successfully, without any errors


Contrail SRIOV boot instance
----------------------------


ID
##

contrail_sriov_boot_snapshot_vm


Description
###########

Launch instance, create snapshot, launch instance from snapshot.


Complexity
##########

advanced


Steps
#####

    1. Create an environment with "Neutron with tunneling segmentation"
       as a network configuration and CEPH storage.
    2. Enable and configure Contrail plugin.
    3. Deploy cluster with some controller+ceph, compute, compute+sriov
       and contrail-specified nodes.
    4. Run OSTF tests.
    5. Setup contrail_sriov_setup.
    6. Create physical network.
    7. Create a subnet.
    8. Create a port.
    9. Boot the instance with the port on the SRIOV host.
    10. Create snapshot of instance.
    11. Launch instance from snapshot.


Expected results
################

All steps must be completed successfully, without any errors.


Contrail SRIOV boot instance from volume
----------------------------------------


ID
##

contrail_sriov_volume


Description
###########

Create volume and boot instance from it.


Complexity
##########

advanced


Steps
#####

    1. Create an environment with "Neutron with tunneling segmentation"
       as a network configuration and CEPH storage.
    2. Enable and configure Contrail plugin.
    3. Deploy cluster with some controller+ceph, compute, compute+sriov and
       contrail-specified nodes.
    4. Run OSTF tests.
    5. Setup contrail_sriov_setup.
    6. Create physical network.
    7. Create a subnet.
    8. Create a port.
    9. Create a new small-size volume from image.
    10. Wait for volume status to become "available".
    11. Launch instance from created volume and port on the SRIOV host.
    12. Wait for "Active" status.
    13. Delete instance.
    14. Delete volume and verify that volume deleted.


Expected results
################

All steps must be completed successfully, without any errors.
