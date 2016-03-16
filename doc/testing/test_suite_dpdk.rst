============
DPDK testing
============


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
        node-03: 'controller';
        node-04: 'compute', 'ceph-osd', 'dpdk';
        node-05: 'compute', 'ceph-osd';
        node-06: 'contrail-db';
        node-07: 'contrail-config';
        node-08: 'contrail-control';
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
        node-2: 'contrail-config', 'contrail-control', 'contrail-db';
        node-3: 'contrail-db';
        node-4: 'compute', 'ceph-osd', 'dpdk';
        node-5: 'compute', 'ceph-osd';
    4. Run OSTF tests
    5. Check Controller and Contrail nodes status
    6. Add one node with following configuration:
        node-6: "compute", "ceph-osd";
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
        node-02: 'contrail-control', 'contrail-config', 'contrail-db';
        node-03: 'contrail-db';
        node-04: 'compute', 'dpdk';
        node-05: 'compute', 'cinder';
        node-06: 'compute';
    4. Run OSTF tests
    5. Delete node-06 with "compute" role
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
        node-01: 'controller';
        node-02: 'contrail-config', 'contrail-control', 'contrail-db';
        node-03: 'contrail-db';
        node-04: 'compute', 'ceph-osd';
        node-05: 'compute', 'ceph-osd';
    4. Run OSTF tests
    6. Add one node with following configuration:
        node-6: 'compute', 'dpdk';
    7. Deploy changes
    8. Run OSTF tests


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
        node-01: 'controller', 'ceph-osd';
        node-02: 'contrail-control', 'contrail-config', 'contrail-db';
        node-03: 'contrail-db';
        node-04: 'compute', 'dpdk', 'ceph-osd';
        node-05: 'compute';
        node-06: 'compute', 'ceph-osd';
    4. Run OSTF tests
    5. Delete node-04 with 'dpdk' and 'compute' roles
    6. Deploy changes
    7. Run OSTF tests


Expected results
################

All steps should pass