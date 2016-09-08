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

    1. Create an environment with "Neutron with tunneling segmentation"
       as a network configuration and CEPH storage
    2. Enable and configure Contrail plugin
    3. Add some controller (at least 3), compute,
       compute with sriov and storage nodes
    4. And contrail-control, contrail-config, contrail-db and contrail-analytics nodes
    5. Deploy cluster
    6. Run OSTF tests
    7. Run contrail check tests
    8. Run contrail health check tests


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

    1. Create an environment with "Neutron with tunneling segmentation"
       as a network configuration and CEPH storage
    2. Enable and configure Contrail plugin with dedicated analytics DB
    3. Deploy cluster with some controller, compute+ceph, compute,
       compute with sriov and contrail-specified nodes
    4. Run OSTF tests
    5. Add a node with compute+ceph roles
    6. Deploy changes
    7. Run OSTF tests
    8. Run contrail check tests
    9. Run contrail health check tests


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

    1. Create an environment with "Neutron with tunneling segmentation"
       as a network configuration and Cinder storage
    2. Enable and configure Contrail plugin
    3. Deploy cluster with some controller, compute, compute+cinder,
       compute, compute with sriov and contrail-specified nodes
    4. Run OSTF tests
    5. Delete a node with compute role
    6. Deploy changes
    7. Run OSTF tests
    8. Run contrail check tests
    9. Run contrail health check tests


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

    1. Create an environment with "Neutron with tunneling segmentation"
       as a network configuration and CEPH+Cinder storage
    2. Enable and configure Contrail plugin with dedicated analytics DB
    3. Deploy cluster with some controller+ceph, compute+ceph, compute,
       compute with sriov and contrail-specified nodes
    4. Run OSTF tests
    5. Run contrail health check tests
    6. Add a node with compute role
    7. Deploy changes
    8. Run OSTF tests
    9. Run contrail health check tests


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

    1. Create an environment with "Neutron with tunneling segmentation"
       as a network configuration and Cinder storage
    2. Enable and configure Contrail plugin with dedicated analytics DB
    3. Deploy cluster with some controller, controller+cinder, compute+cinder,
       compute, compute with sriov and contrail-specified nodes
    4. Run OSTF tests
    5. Run contrail health check tests
    6. Delete a node with compute roles
    7. Deploy changes
    8. Run OSTF tests
    9. Run contrail health check tests


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

    1. Deploy cluster with some controller, compute+cinder,
       compute, compute with sriov and contrail-specified nodes
    2. Run 'fuel-mirror create -P ubuntu -G mos ubuntu' on the master node
    3. Run 'fuel-mirror apply -P ubuntu -G mos ubuntu --env <env_id> --replace' on the master node
    4. Update repos for all deployed nodes with command
       "fuel --env <env_id> node --node-id 1,2,3,4,5,6,7,9,10 --tasks setup_repositories" on the master node
    5. Run OSTF and check Contrail node status.


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

    1. Create an environment with "Neutron with tunneling segmentation"
       as a network configuration and CEPH storage
    2. Enable and configure Contrail plugin with dedicated analytics DB
    3. Deploy cluster with some controller, compute+ceph,
       compute, compute with sriov and contrail-specified nodes
    4. Run OSTF tests
    5. Add a node with controller+ceph role
    6. Deploy changes
    7. Run OSTF tests
    8. Run contrail health check tests


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

    1. Create an environment with "Neutron with tunneling segmentation"
       as a network configuration and Cinder storage
    2. Enable and configure Contrail plugin
    3. Deploy cluster with some controller, compute+cinder, compute,
       compute with sriov and contrail-specified nodes
    4. Run OSTF tests
    5. Delete a node with "controller" role
    6. Deploy changes
    7. Run OSTF tests
    8. Run contrail health check tests


Expected results
################

All steps must be completed successfully, without any errors


Contrail SRIOV boot instance
----------------------------


ID
##

test_sriov_boot_snapshot_vm


Description
###########

Launch instance, create snapshot, launch instance from snapshot.


Complexity
##########

advanced


Steps
#####

    1. Create physical network.
    2. Create a subnet.
    3. Create a port.
    4. Boot the instance with the port on the SRIOV host.
    5. Create snapshot of instance.
    6. Delete the instance created in step 5.
    7. Launch instance from snapshot.
    8. Delete the instance created in step 7.


Expected results
################

All steps must be completed successfully, without any errors.


Contrail SRIOV boot instance from volume
----------------------------------------


ID
##

test_sriov_volume


Description
###########

Create volume and boot instance from it.


Complexity
##########

advanced


Steps
#####

    1. Create physical network.
    2. Create a subnet.
    3. Create a port.
    4. Create a new small-size volume from image.
    5. Wait for volume status to become "available".
    6. Launch instance from created volume and port on the SRIOV host.
    7. Wait for "Active" status.
    8. Delete instance.
    9. Delete volume and verify that volume deleted..


Expected results
################

All steps must be completed successfully, without any errors.
