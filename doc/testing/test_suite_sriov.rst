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