===========
SRIOV Tests
===========


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
3. Deploy cluster with following node configuration:
    node-1: controller
    node-2: controller
    node-3: controller
    node-4: compute, sriov
    node-5: compute
    node-6: compute
    node-7: contrail-db, contrail-config, contrail-control
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
3. Deploy cluster with following node configuration:
    node-1: controller, ceph-osd
    node-2: contrail-config, contrail-control, contrail-db
    node-3: contrail-db
    node-4: compute, ceph-osd
    node-5: compute, sriov, ceph-osd
4. Run OSTF tests
5. Add node with role:
    node-6: compute, ceph-osd
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
3. Deploy cluster with following node configuration:
    node-1: controller
    node-2: contrail-config, contrail-control, contrail-db
    node-3: contrail-db
    node-4: compute, cinder
    node-5: compute, cinder, sriov
4. Run OSTF tests
5. Delete node with role:
    node-6: compute
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
3. Deploy cluster with following node configuration:
    node-1: controller
    node-2: contrail-config, contrail-control, contrail-db
    node-3: contrail-db
    node-4: compute, ceph-osd
    node-5: compute, ceph-osd
4. Run OSTF tests
5. Add node with role:
    node-6: compute, sriov
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
3. Deploy cluster with following node configuration:
    node-1: controller, ceph-osd
    node-2: contrail-config, contrail-control, contrail-db
    node-3: contrail-db
    node-4: compute, sriov, ceph-osd
    node-6: compute, ceph-osd
4. Run OSTF tests
5. Delete node with role sriov:
    node-4: compute, sriov, ceph-osd
6. Deploy changes
7. Run OSTF tests


Expected results
################

All steps must be completed successfully, without any errors.