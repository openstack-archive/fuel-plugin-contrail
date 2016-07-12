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
    3. Deploy cluster with following node configuration:
        node-01: 'controller';
        node-02: 'controller';
        node-03: 'controller', 'ceph-osd';
        node-04: 'compute', 'ceph-osd';
        node-05: 'compute', 'ceph-osd';
        node-07: 'contrail-db';
        node-08: 'contrail-config';
        node-09: 'contrail-control';
        node-dpdk: 'compute', dpdk';
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
    3. Deploy cluster with following node configuration:
        node-1: 'controller', 'ceph-osd';
        node-2: 'contrail-config', 'contrail-control',
            'contrail-db', 'contrail-analytics';
        node-3: 'compute', 'ceph-osd';
        node-4: 'compute', 'ceph-osd';
        node-dpdk: 'compute', 'dpdk';
    4. Run OSTF tests
    5. Add one node with following configuration:
        node-5: "compute", "ceph-osd";
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
    3. Deploy cluster with following node configuration:
        node-01: 'controller';
        node-02: 'contrail-control', 'contrail-config', 'contrail-db', 'contrail-analytics';
        node-03: 'contrail-db';
        node-04: 'compute', 'cinder';
        node-05: 'compute';
        node-06: 'contrail-db';
    4. Run OSTF tests
    5. Delete node-05 with "compute" role
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
    3. Deploy cluster with following node configuration:
        node-01: 'controller', 'ceph-osd';
        node-02: 'contrail-config', 'contrail-control',
            'contrail-db', 'contrail-analytics';
        node-03: 'compute', 'ceph-osd';
        node-04: 'compute', 'ceph-osd';
        node-05: 'controller', 'cinder';
        node-06: 'controller', 'cinder';
    4. Run OSTF tests
    6. Add one node with following configuration:
        node-dpdk: "compute", "dpdk";
    7. Deploy changes
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
    3. Deploy cluster with following node configuration:
        node-01: 'controller', 'ceph-osd', 'cinder';
        node-02: 'contrail-control', 'contrail-config',
            'contrail-db', 'contrail-analytics';
        node-03: 'compute', 'ceph-osd';
        node-04: 'compute', 'ceph-osd';
        node-dpdk: 'compute', 'dpdk';
    4. Run OSTF tests
    5. Delete node "node-dpdk" with "dpdk" and "compute" roles
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
    3. Deploy cluster with following node configuration:
        node-1: 'controller', 'ceph-osd';
        node-2: 'contrail-config', 'contrail-control',
            'contrail-db', 'contrail-analytics';
        node-3: 'compute', 'ceph-osd';
        node-4: 'compute', 'ceph-osd';
    4. Run OSTF tests
    5. Add one node with following configuration:
        node-5: 'controller', 'ceph-osd';
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
    3. Deploy cluster with following node configuration:
        node-01: 'controller';
        node-02: 'contrail-control', 'contrail-config',
            'contrail-db', 'contrail-analytics';
        node-03: 'controller';
        node-04: 'compute', 'cinder';
        node-05: 'controller';
    4. Run OSTF tests
    5. Delete node-01 with "controller" role
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
    4. Add dpdk and sriov nodes
    5. Deploy cluster with following node configuration:
        node-2: 'contrail-config', 'contrail-control',
            'contrail-db', 'contrail-analytics';
        node-3: 'compute', 'cinder';
        node-4: 'contrail-config', 'contrail-control',
            'contrail-db', 'contrail-analytics';
        node-5: 'contrail-config', 'contrail-control',
            'contrail-db', 'contrail-analytics';
    6. Deploy cluster
    7. Run OSTF
    8. Add one node with following configuration:
        node-1: 'controller';
    9. Deploy changes


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
