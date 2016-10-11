==========
DPDK on VF
==========


Contrail HA DPDK on VF
----------------------


ID
##

contrail_ha_dpdk_on_vf


Description
###########

Check Contrail deploy on HA environment


Complexity
##########

advanced


Steps
#####

    1. Create an environment with "Neutron with tunneling
       segmentation" as a network configuration and CEPH storage
    2. Enable and configure Contrail plugin
    3. Enable DPDK on VF feature
    4. Deploy cluster with following node configuration:
       node-01: 'controller';
       node-02: 'controller';
       node-03: 'controller', 'ceph-osd';
       node-04: 'compute', 'ceph-osd';
       node-05: 'compute', 'ceph-osd';
       node-06: 'contrail-controller';
       node-07: 'contrail-analytics';
       node-08: 'contrail-analytics-db';
       node-dpdk: 'compute', dpdk';
    5. Run OSTF tests
    6. Run contrail health check tests


Expected results
################

All steps should pass


Contrail DPDK on VF add compute
-------------------------------


ID
##

contrail_dpdk_on_vf_add_compute


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
    3. Enable DPDK on VF feature
    4. Deploy cluster with following node configuration:
       node-1: 'controller', 'ceph-osd';
       node-2: 'contrail-controller';
       node-3: 'compute', 'ceph-osd';
       node-4: 'contrail-analytics', 'contrail-analytics-db';
       node-dpdk: 'compute', 'dpdk';
    5. Run OSTF tests
    6. Add one node with following configuration:
       node-5: "compute", "ceph-osd";
    7. Deploy changes
    8. Run OSTF tests
    9. Run contrail health check tests


Expected results
################

All steps should pass


Contrail DPDK on VF delete compute
----------------------------------


ID
##

contrail_dpdk_on_vf_delete_compute


Description
###########

Verify that Contrail compute role can be deleted after deploying


Complexity
##########

advanced


Steps
#####

    1. Create an environment with "Neutron with tunneling
       segmentation" as a network configuration
    2. Enable and configure Contrail plugin
    3. Enable DPDK on VF feature
    4. Deploy cluster with following node configuration:
       node-01: 'controller';
       node-02: 'contrail-controller';
       node-03: 'contrail-controller';
       node-04: 'compute', 'cinder';
       node-05: 'compute';
       node-06: 'contrail-analytics', 'contrail-analytics-db';
    5. Run OSTF tests
    6. Delete node-05 with "compute" role
    7. Deploy changes
    8. Run OSTF tests
    9. Run contrail health check tests


Expected results
################

All steps should pass


Contrail DPDK on VF add dpdk
----------------------------


ID
##

contrail_dpdk_on_vf_add_dpdk


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
    3. Enable DPDK on VF feature
    4. Deploy cluster with following node configuration:
       node-01: 'controller', 'ceph-osd';
       node-02: 'contrail-controller';
       node-03: 'compute', 'ceph-osd';
       node-04: 'compute', 'ceph-osd';
       node-05: 'controller', 'cinder';
       node-06: 'controller', 'cinder';
       node-07: 'contrail-analytics';
       node-08: 'contrail-analytics-db';
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


Contrail DPDK on VF delete dpdk
-------------------------------


ID
##

contrail_dpdk_on_vf_delete_dpdk


Description
###########

Verify that DPDK role can be deleted after deploying


Complexity
##########

advanced


Steps
#####

    1. Create an environment with "Neutron with tunneling
       segmentation" as a network configuration
    2. Enable and configure Contrail plugin
    3. Enable DPDK on VF feature
    4. Deploy cluster with following node configuration:
       node-01: 'controller', 'ceph-osd', 'cinder';
       node-02: 'contrail-controller';
       node-03: 'compute', 'ceph-osd';
       node-04: 'compute', 'ceph-osd';
       node-05: 'contrail-analytics', 'contrail-analytics-db';
       node-dpdk: 'compute', 'dpdk';
    5. Run OSTF tests
    6. Run contrail health check tests
    7. Delete node "node-dpdk" with "dpdk" and "compute" roles
    8. Deploy changes
    9. Run OSTF tests
    10. Run contrail health check tests


Expected results
################

All steps should pass


Contrail DPDK on VF add controller
----------------------------------


ID
##

contrail_dpdk_on_vf_add_controller


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
    3. Enable DPDK on VF feature
    4. Deploy cluster with following node configuration:
       node-1: 'controller', 'ceph-osd';
       node-2: 'contrail-controller';
       node-3: 'compute', 'ceph-osd';
       node-4: 'compute', 'ceph-osd';
       node-5: 'contrail-analytics', 'contrail-analytics-db';
       node-6: 'contrail-analytics';
    5. Run OSTF tests
    6. Run contrail health check tests
    7. Add one node with following configuration:
       node-7: 'controller', 'ceph-osd';
    8. Deploy changes
    9. Run OSTF tests
    10. Run contrail health check tests


Expected results
################

All steps must be completed successfully, without any errors


Contrail DPDK on VF delete controller
-------------------------------------


ID
##

contrail_dpdk_on_vf_delete_controller


Description
###########

Verify that controller node can be deleted after deploy


Complexity
##########

advanced


Steps
#####

    1. Create an environment with "Neutron with tunneling
       segmentation" as a network configuration
    2. Enable and configure Contrail plugin
    3. Enable DPDK on VF feature
    4. Deploy cluster with following node configuration:
       node-01: 'controller';
       node-02: 'contrail-controller';
       node-03: 'controller';
       node-04: 'compute', 'cinder';
       node-05: 'controller';
       node-06: 'contrail-analytics', 'contrail-analytics-db';
       node-07: 'contrail-analytics-db';
       node-08: 'contrail-analytics-db';
    5. Run OSTF tests
    6. Delete node-01 with "controller" role
    7. Deploy changes
    8. Run OSTF tests
    9. Run contrail health check tests


Expected results
################

All steps must be completed successfully, without any errors
