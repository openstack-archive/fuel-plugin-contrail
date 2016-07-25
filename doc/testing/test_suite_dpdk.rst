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
    3. Add dpdk and sriov nodes
    4. Deploy cluster with following node configuration:
       node-1: 'controller';
       node-2: 'contrail-config', 'contrail-control',
               'contrail-db', 'contrail-analytics';
       node-3: 'compute', 'cinder',
    5. Deploy cluster
    6. Run OSTF
    7. Add nodes with configurations:
       node-4: 'contrail-config', 'contrail-control',
               'contrail-db', 'contrail-analytics';
       node-5: 'contrail-config', 'contrail-control',
               'contrail-db', 'contrail-analytics';
    8. Deploy changes
    9. Run OSTF


Expected results
################

All steps must be completed successfully, without any errors.
