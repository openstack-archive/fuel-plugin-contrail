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
       node-06: 'contrail-db';
       node-07: 'contrail-config';
       node-08: 'contrail-control';
       node-09: 'contrail-analytics', 'contrail-analytics-db';
       node-dpdk: 'compute', dpdk';
    4. Run OSTF tests
    5. Run contrail health check tests


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

    1. Create an environment with "Neutron with tunneling
       segmentation" as a network configuration
    2. Enable and configure Contrail plugin
    3. Enable dedicated analytics DB
    4. Deploy cluster with following node configuration:
        node-1: 'controller', 'ceph-osd';
        node-2: 'contrail-config', 'contrail-control',
            'contrail-db';
        node-3: 'compute', 'ceph-osd';
        node-4: 'compute', 'ceph-osd';
        node-5: 'compute', 'ceph-osd';
        node-dpdk: 'compute', 'dpdk';
        node-7: 'contrail-analytics', 'contrail-analytics-db';
    5. Run OSTF tests
    6. Add one node with following configuration:
        node-5: "compute", "ceph-osd";
    7. Deploy changes
    8. Run OSTF tests
    9. Run contrail health check tests


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
    8. Run contrail health check tests


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

    1. Create an environment with "Neutron with tunneling
       segmentation" as a network configuration
    2. Enable and configure Contrail plugin
    3. Enable dedicated analytics DB
    4. Deploy cluster with following node configuration:
        node-01: 'controller', 'ceph-osd';
        node-02: 'contrail-config', 'contrail-control',
            'contrail-db', 'contrail-analytics';
        node-03: 'compute', 'ceph-osd';
        node-04: 'compute', 'ceph-osd';
        node-05: 'controller', 'cinder';
        node-06: 'controller', 'cinder';
        node-07: 'contrail-analytics-db';
    5. Run OSTF tests
    6. Run contrail health check tests
    7. Add one node with following configuration:
        node-dpdk: "compute", "dpdk";
    8. Deploy changes
    9. Run OSTF tests
    10. Run contrail health check tests


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
       node-02: 'contrail-control', 'contrail-config', 'contrail-db', 'contrail-analytics';
       node-03: 'compute', 'ceph-osd';
       node-04: 'compute', 'ceph-osd';
       node-dpdk: 'compute', 'dpdk';
    4. Run OSTF tests
    5. Run contrail health check tests
    6. Delete node "node-dpdk" with "dpdk" and "compute" roles
    7. Deploy changes
    8. Run OSTF tests
    9. Run contrail health check tests


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
    2. Run 'fuel-mirror create -P ubuntu -G mos ubuntu' on the master node
    3. Run 'fuel-mirror apply -P ubuntu -G mos ubuntu --env <env_id> --replace' on the master node
    4. Update repos for all deployed nodes with command "fuel --env <env_id> node --node-id 1,2,3,4,5,6,7,9,10 --tasks setup_repositories" on the master node
    5. Run OSTF and check Contrail node status.


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

    1. Create an environment with "Neutron with tunneling
       segmentation" as a network configuration
    2. Enable and configure Contrail plugin
    3. Enable dedicated analytics DB
    4. Deploy cluster with following node configuration:
        node-1: 'controller', 'ceph-osd';
        node-2: 'contrail-config', 'contrail-control',
            'contrail-db', 'contrail-analytics';
        node-3: 'compute', 'ceph-osd';
        node-4: 'compute', 'ceph-osd';
        node-6: 'contrail-analytics', 'contrail-analytics-db';
    5. Run OSTF tests
    6. Add one node with following configuration:
        node-5: 'controller', 'ceph-osd';
    7. Deploy changes
    8. Run OSTF tests
    9. Run contrail health check tests


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
       node-02: 'contrail-control', 'contrail-config', 'contrail-db', 'contrail-analytics';
       node-03: 'controller';
       node-04: 'compute', 'cinder';
       node-05: 'controller';
    4. Run OSTF tests
    5. Delete node-01 with "controller" role
    6. Deploy changes
    7. Run OSTF tests
    8. Run contrail health check tests


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

    1. Create an environment with "Neutron with tunneling segmentation"
        as a network configuration
    2. Enable and configure Contrail plugin
    3. Enable dedicated analytics DB
    4. Add dpdk and sriov nodes
    5. Deploy cluster with following node configuration:
       node-1: 'controller';
       node-2: 'contrail-config', 'contrail-control',
               'contrail-db', 'contrail-analytics';
       node-3: 'compute', 'cinder',
    6. Deploy cluster
    7. Run OSTF
    8. Add nodes with configurations:
       node-4: 'contrail-config', 'contrail-control',
               'contrail-db', 'contrail-analytics';
       node-5: 'contrail-config', 'contrail-control',
               'contrail-db', 'contrail-analytics';
       node-6: 'contrail-analytics-db';
    9. Deploy changes
    10. Run OSTF
    11. Run contrail health check tests

Expected results
################

All steps must be completed successfully, without any errors.


Contrail DPDK boot instance
---------------------------


ID
##

test_dpdk_boot_snapshot_vm


Description
###########

Launch instance, create snapshot, launch instance from snapshot.


Complexity
##########

advanced


Steps
#####

    1. Create no default network with subnet.
    2. Get existing flavor with hpgs.
    3. Launch an instance using the default image and flavor with hpgs
       in the hpgs availability zone.
    4. Make snapshot of the created instance.
    5. Delete the last created instance.
    6. Launch another instance from the snapshot created in step 4
       and flavor with hpgs in the hpgs availability zone.
    7. Delete the last created instance.


Expected results
################

All steps must be completed successfully, without any errors.


Contrail DPDK boot instance from volume
---------------------------------------


ID
##

test_dpdk_volume


Description
###########

Create volume and boot instance from it.


Complexity
##########

advanced


Steps
#####

    1. Create no default network with subnet.
    2. Get existing flavor with hpgs.
    3. Create a new small-size volume from image.
    4. Wait for volume status to become "available".
    5. Launch an instance using the default image and flavor with hpgs
       in the hpgs availability zone.
    6. Wait for "Active" status.
    7. Delete the last created instance.
    8. Delete volume and verify that volume deleted.


Expected results
################

All steps must be completed successfully, without any errors.


Contrail DPDK Check network connectivity from instance via floating IP
----------------------------------------------------------------------


ID
##

test_dpdk_check_public_connectivity_from_instance


Description
###########

Check network connectivity from instance via floating IP


Complexity
##########

advanced


Steps
#####

    1. Create no default network with subnet.
    2. Create Router_01, set gateway and add interface
       to external network.
    3. Get existing flavor with hpgs.
    4. Create a new security group (if it doesn`t exist yet).
    5. Launch an instance using the default image and flavor with hpgs
       in the hpgs availability zone.
    6. Create a new floating IP.
    7. Assign the new floating IP to the instance.
    8. Check connectivity to the floating IP using ping command.
    9. Check that public IP 8.8.8.8 can be pinged from instance.
    10. Delete instance.


Expected results
################

All steps must be completed successfully, without any errors.
