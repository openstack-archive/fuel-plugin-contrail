====
DPDK
====


Contrail HA DPDK
----------------


ID
##

contrail_ha_dpdk


Description
###########

Check Contrail deploy on HA environment


Complexity
##########

advanced


Steps
#####

    1. Create an environment with "Neutron with tunneling segmentation" as a network configuration and CEPH storage
    2. Enable and configure Contrail plugin
    3. Deploy cluster with some controller+mongo, compute+ceph-osd, compute+dpdk and contrail-specified nodes
    4. Run OSTF tests


Expected results
################

All steps should pass


Contrail DPDK add compute
-------------------------


ID
##

contrail_dpdk_add_compute


Description
###########

Verify that Contrail compute role can be added after deploying


Complexity
##########

advanced


Steps
#####

    1. Create an environment with "Neutron with tunneling segmentation" as a network configuration
    2. Enable and configure Contrail plugin
    3. Deploy cluster with some controller+mongo, compute+ceph-osd, compute+dpdk and contrail-specified nodes
    4. Run OSTF tests
    5. Check Controller and Contrail nodes status
    6. Add one node with "compute+ceph-osd" role
    7. Deploy changes
    8. Run OSTF tests


Expected results
################

All steps should pass


Contrail DPDK delete compute
----------------------------


ID
##

contrail_dpdk_delete_compute


Description
###########

Verify that Contrail compute role can be deleted after deploying


Complexity
##########

advanced


Steps
#####

    1. Create an environment with "Neutron with tunneling segmentation" as a network configuration
    2. Enable and configure Contrail plugin
    3. Deploy cluster with some controller+mongo, compute+ceph-osd, compute+dpdk and contrail-specified nodes
    4. Run OSTF tests
    5. Delete node with "compute" role
    6. Deploy changes
    7. Run OSTF tests


Expected results
################

All steps should pass


Contrail DPDK add dpdk
----------------------


ID
##

contrail_dpdk_add_dpdk


Description
###########

Verify that DPDK role can be added after deploying


Complexity
##########

advanced


Steps
#####

    1. Create an environment with "Neutron with tunneling segmentation" as a network configuration
    2. Enable and configure Contrail plugin
    3. Deploy cluster with some controller+mongo, compute+ceph-osd, compute+dpdk and contrail-specified nodes
    4. Run OSTF tests
    5. Add a node with "compute+dpdk" roles
    6. Deploy changes
    7. Run OSTF tests


Expected results
################

All steps should pass


Contrail DPDK delete dpdk
-------------------------


ID
##

contrail_dpdk_delete_dpdk


Description
###########

Verify that DPDK role can be deleted after deploying


Complexity
##########

advanced


Steps
#####

    1. Create an environment with "Neutron with tunneling segmentation" as a network configuration
    2. Enable and configure Contrail plugin
    3. Deploy cluster with some controller+mongo, compute+ceph-osd, compute+dpdk and contrail-specified nodes
    4. Run OSTF tests
    5. Delete node with compute+dpdk roles
    6. Deploy changes
    7. Run OSTF tests


Expected results
################

All steps should pass


Check updating core repos with Contrail plugin and DPDK
-------------------------------------------------------


ID
##

contrail_dpdk_update_core_repos


Description
###########

Check updating core repos with Contrail plugin and DPDK


Complexity
##########

advanced


Steps
#####

    1. Deploy cluster with some controller+mongo, compute+ceph-osd, compute+dpdk and contrail-specified nodes
    2. Run “fuel-createmirror -M” on the master node
    3. Update repos for all deployed nodes with command "fuel --env <ENV_ID> node --node-id <NODE_ID1>, <NODE_ID2>, <NODE_ID_N> --tasks upload_core_repos" on the master node


Expected results
################

All steps must be completed successfully, without any errors


Contrail DPDK add controller
----------------------------


ID
##

contrail_dpdk_add_controller


Description
###########

Verify that controller node can be added after deploy


Complexity
##########

advanced


Steps
#####

    1. Create an environment with "Neutron with tunneling segmentation" as a network configuration
    2. Enable and configure Contrail plugin
    3. Deploy cluster with some controller+mongo, compute+ceph-osd, compute+dpdk and contrail-specified nodes
    4. Run OSTF tests
    5. Add node with "controller" role
    6. Deploy changes
    7. Run OSTF tests


Expected results
################

All steps must be completed successfully, without any errors


Contrail DPDK delete controller
-------------------------------


ID
##

contrail_dpdk_delete_controller


Description
###########

Verify that controller node can be deleted after deploy


Complexity
##########

advanced


Steps
#####

    1. Create an environment with "Neutron with tunneling segmentation" as a network configuration
    2. Enable and configure Contrail plugin
    3. Deploy cluster with some controller, controller+mongo, compute+ceph-osd, compute+dpdk and contrail-specified nodes
    4. Run OSTF tests
    5. Delete node with "controller" role
    6. Deploy changes
    7. Run OSTF tests


Expected results
################

All steps must be completed successfully, without any errors


Verify that contrail nodes can be added after deploying with dpdk and sriov
---------------------------------------------------------------------------


ID
##

contrail_add_to_dpdk_sriov


Description
###########

Verify that contrail nodes can be added after deploying with dpdk and sriov


Complexity
##########

Advanced


Steps
#####

    1. Create an environment with "Neutron with tunneling segmentation" as a network configuration
    2. Enable and configure Contrail plugin
    3. Enable dpdk and sriov
    4. Add some controller, compute nodes with storage
    5. Add dpdk node
    6. Add sriov node
    7. Deploy cluster
    8. Run OSTF
    9. Add "contrail-config", "contrail-control", "contrail-db" roles
    10. Deploy changes
    11. Run OSTF


Expected results
################

All steps must be completed successfully, without any errors.


Contrail DPDK boot instance
---------------------------


ID
##

contrail_dpdk_boot_snapshot_vm


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
    3. Enable dpdk.
    4. Deploy cluster with some controller+ceph, compute, compute+dpdk
       and contrail-specified nodes.
    5. Run OSTF tests.
    6. Create no default network with subnet.
    7. Get existing flavor with hpgs.
    8. Launch an instance using the default image and flavor with hpgs
       in the hpgs availability zone.
    9. Make snapshot of the created instance.
    10. Delete the last created instance.
    11. Launch another instance from the snapshot created in step 2
       and flavor with hpgs in the hpgs availability zone.
    12. Delete the last created instance..


Expected results
################

All steps must be completed successfully, without any errors.


Contrail DPDK boot instance from volume
---------------------------------------


ID
##

contrail_dpdk_volume


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
    3. Enable dpdk
    4. Deploy cluster with some controller+ceph, compute, compute+dpdk and
       contrail-specified nodes.
    5. Run OSTF tests.
    6. Create no default network with subnet.
    7. Get existing flavor with hpgs.
    8. Create a new small-size volume from image.
    9. Wait for volume status to become "available".
    10. Launch an instance using the default image and flavor with hpgs
       in the hpgs availability zone.
    11. Wait for "Active" status.
    12. Delete the last created instance.
    13. Delete volume and verify that volume deleted.


Expected results
################

All steps must be completed successfully, without any errors.


Contrail DPDK Check network connectivity from instance via floating IP
----------------------------------------------------------------------


ID
##

contrail_dpdk_check_public_connectivity_from_instance


Description
###########

Check network connectivity from instance via floating IP


Complexity
##########

advanced


Steps
#####

    1. Create an environment with "Neutron with tunneling segmentation"
       as a network configuration and CEPH storage.
    2. Enable and configure Contrail plugin.
    3. Enable dpdk
    4. Deploy cluster with some controller+ceph, compute, compute+dpdk and
       contrail-specified nodes.
    5. Run OSTF tests.
    6. Create no default network with subnet.
    7. Create Router_01, set gateway and add interface
       to external network.
    8. Get existing flavor with hpgs.
    9. Create a new security group (if it doesn`t exist yet).
    10. Launch an instance using the default image and flavor with hpgs
        in the hpgs availability zone.
    11. Create a new floating IP.
    12. Assign the new floating IP to the instance.
    13. Check connectivity to the floating IP using ping command.
    14. Check that public IP 8.8.8.8 can be pinged from instance.
    15. Delete instance.


Expected results
################

All steps must be completed successfully, without any errors.
