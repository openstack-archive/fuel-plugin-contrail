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

    1. Create an environment with "Neutron with tunneling segmentation" as a network configuration and CEPH storage
    2. Enable and configure Contrail plugin
    3. Add some controller (at least 3), compute and storage nodes
    4. And contrail-control, contrail-config, contrail-db and contrail-analytics nodes
    5. Deploy cluster
    6. Run OSTF tests


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
    3. Deploy cluster with some controller, compute+ceph, compute+sriov and contrail-specified nodes
    4. Run OSTF tests
    5. Add a node with compute+ceph roles
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
    3. Deploy cluster with some controller, compute, compute+cinder, compute+sriov and contrail-specified nodes
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

    1. Create an environment with "Neutron with tunneling segmentation" as a network configuration and CEPH+Cinder storage
    2. Enable and configure Contrail plugin
    3. Deploy cluster with some controller+ceph, compute+ceph, compute+sriov and contrail-specified nodes
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

    1. Create an environment with "Neutron with tunneling segmentation" as a network configuration and Cinder storage
    2. Enable and configure Contrail plugin
    3. Deploy cluster with some controller, controller+cinder, compute+cinder, compute+sriov and contrail-specified nodes
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
    3. Deploy cluster with some controller, compute+ceph, compute+sriov and contrail-specified nodes
    4. Run OSTF tests
    5. Add a node with controller+ceph role
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

    1. Create an environment with "Neutron with tunneling segmentation" as a network configuration and Cinder storage
    2. Enable and configure Contrail plugin
    3. Deploy cluster with some controller, compute+cinder, compute+sriov and contrail-specified nodes
    4. Run OSTF tests
    5. Delete a node with "controller" role
    6. Deploy changes
    7. Run OSTF tests


Expected results
################

All steps must be completed successfully, without any errors
