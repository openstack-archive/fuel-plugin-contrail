=======
DPDK VF
=======


Contrail HA DPDK VF SRIOV
-------------------------


ID
##

contrail_ha_dpdk_vf


Description
###########

Check Contrail deploy on HA environment with DPDK VF


Complexity
##########

advanced


Steps
#####

    1. Create an environment with "Neutron with tunneling segmentation"
       as a network configuration and CEPH storage
    2. Enable and configure Contrail plugin:
         enable dpdk
         enable sriov
         enable DPDK on VF
    3. Add following nodes:
         3 controller + mongo
         1 compute + ceph
         1 contrail-config+contrail-control+contrail-db
         1 compute+sriov+dpdk
    4. Deploy cluster.
    5. Run OSTF tests.

Expected results
################

All steps should pass


Contrail DPDK on VF add compute
-------------------------


ID
##

contrail_dpdk_vf_add_compute


Description
###########

Verify that compute node can be added after deploying


Complexity
##########

advanced


Steps
#####

    1. Create an environment with "Neutron with tunneling segmentation"
       as a network configuration
    2. Enable and configure Contrail plugin:
         enable dpdk
         enable sriov
         enable DPDK on VF
    3. Add following nodes:
         1 controller
         1 compute+sriov+dpdk
         1 contrail-config+contrail-control+contrail-db
    4. Deploy cluster.
    5. Run OSTF tests.
    5. Check Controller and Contrail nodes status.
    6. Add one node with compute role.
    7. Deploy changes.
    8. Run OSTF tests.


Expected results
################

All steps should pass


Contrail DPDK on VF delete compute
----------------------------------


ID
##

contrail_dpdk_vf_delete_compute


Description
###########

Verify that Contrail compute role can be deleted after deploying


Complexity
##########

advanced


Steps
#####

    1. Create an environment with "Neutron with tunneling segmentation"
       as a network configuration
    2. Enable and configure Contrail plugin:
         enable dpdk
         enable sriov
         enable DPDK on VF
    3. Add following nodes:
         1 controller
         1 compute
         1 contrail-config+contrail-control+contrail-db
         1 compute+sriov+dpdk
    4. Run OSTF tests.
    5. Delete node with compute role.
    6. Deploy changes.
    7. Run OSTF tests.


Expected results
################

All steps should pass


Contrail DPDK on VF add dpdk
----------------------


ID
##

contrail_dpdk_vf_add_dpdk_sriov


Description
###########

Verify that DPDK SRIOV role can be added after deploying


Complexity
##########

advanced


Steps
#####

    1. Create an environment with "Neutron with tunneling segmentation"
       as a network configuration
    2. Enable and configure Contrail plugin:
         enable dpdk
         enable sriov
         enable DPDK on VF
    3. Add following nodes:
         1 controller
         1 compute+sriov+dpdk
         1 contrail-config+contrail-control+contrail-db
    4. Run OSTF tests.
    5. Add a node with compute+dpdk+sriov roles.
    6. Deploy changes.
    7. Run OSTF tests.


Expected results
################

All steps should pass


Contrail DPDK on VF delete dpdk sriov
-------------------------------------


ID
##

contrail_dpdk_vf_delete_dpdk_sriov


Description
###########

Verify that DPDK SRIOV role can be deleted after deploying


Complexity
##########

advanced


Steps
#####

    1. Create an environment with "Neutron with tunneling segmentation"
       as a network configuration
    2. Enable and configure Contrail plugin:
         enable dpdk
         enable sriov
         enable DPDK on VF
    3. Add following nodes:
         1 controller
         2 compute+sriov+dpdk
         1 contrail-config+contrail-control+contrail-db
    4. Run OSTF tests.
    5. Delete node with compute+dpdk roles.
    6. Deploy changes.
    7. Run OSTF tests.


Expected results
################

All steps should pass


Contrail DPDK on VF add controller
----------------------------


ID
##

contrail_dpdk_vf_add_controller


Description
###########

Verify that controller node can be added after deploy


Complexity
##########

advanced


Steps
#####

    1. Create an environment with "Neutron with tunneling segmentation"
       as a network configuration
    2. Enable and configure Contrail plugin:
         enable dpdk
         enable sriov
         enable DPDK on VF
    3. Add following nodes:
         1 controller
         1 compute+sriov+dpdk
         1 contrail-config+contrail-control+contrail-db
    4. Run OSTF tests.
    5. Add node with controller role.
    6. Deploy changes.
    7. Run OSTF tests.


Expected results
################

All steps must be completed successfully, without any errors


Contrail DPDK on VF delete controller
-------------------------------


ID
##

contrail_dpdk_vf_delete_controller


Description
###########

Verify that controller node can be deleted after deploy


Complexity
##########

advanced


Steps
#####

    1. Create an environment with "Neutron with tunneling segmentation"
       as a network configuration.
    2. Enable and configure Contrail plugin:
         enable dpdk
         enable sriov
         enable DPDK on VF
    3. Add following nodes:
         3 controller
         1 compute+sriov+dpdk
         1 contrail-config+contrail-control+contrail-db
    4. Run OSTF tests.
    5. Delete node with controller role.
    6. Deploy changes.
    7. Run OSTF tests.


Expected results
################

All steps must be completed successfully, without any errors


Verify that contrail nodes can be added after deploying with dpdk and sriov
---------------------------------------------------------------------------


ID
##

contrail_add_to_dpdk_vf_sriov


Description
###########

Verify that contrail nodes can be added after deploying with dpdk and sriov


Complexity
##########

Advanced


Steps
#####

    1. Create an environment with "Neutron with tunneling segmentation"
       as a network configuration.
    2. Enable and configure Contrail plugin:
         enable dpdk
         enable sriov
         enable DPDK on VF
    3. Add following nodes:
         1 controller
         1 compute
         1 contrail-config+contrail-control+contrail-db
         1 compute+sriov+dpdk
    4. Deploy cluster.
    5. Run OSTF.
    6. Add "contrail-config", "contrail-control", "contrail-db" roles.
    7. Deploy changes.
    8. Run OSTF.


Expected results
################

All steps must be completed successfully, without any errors.


Contrail DPDK on VF connection between instances
---------------------------------------------- -


ID
##

contrail_dpdk_vf_connection


Description
###########

Check connection between instances from different availibility zone


Complexity
##########

advanced


Steps
#####

    1. Create an environment with "Neutron with tunneling segmentation"
       as a network configuration and CEPH storage
    2. Enable and configure Contrail plugin:
         enable dpdk
         enable sriov
         enable DPDK on VF
    3. Add following nodes:
         1 controller
         1 compute + ceph
         1 contrail-config+contrail-control+contrail-db
         1 compute+sriov+dpdk
    4. Deploy cluster.
    5. Run OSTF tests
    6. Create private networks net01 with subnet.
    7. Add one  subnet (net01_subnet01: 192.168.101.0/24.
    8. Create Router_01, set gateway and add interface
       to external network.
    9. Launch few instances in the net01.
       with image TestVM and flavor m1.micro in nova az.
    10. Launch few instances in the net01.
        with image TestVM and flavor m1.small.hpgs in hpgs az.
    11. Check connection between instances (ping, ssh).

Expected results
################

All steps should pass

Contrail DPDK on rebbot
---------------------------------------------- -


ID
##

contrail_dpdk_vf_rebbot


Description
###########

Check DPDK on VF functionality after reboot node DPDK+SRIOV


Complexity
##########

advanced


Steps
#####

    1. Create an environment with "Neutron with tunneling segmentation"
       as a network configuration and CEPH storage
    2. Enable and configure Contrail plugin:
         enable dpdk
         enable sriov
         enable DPDK on VF
    3. Add following nodes:
         1 controller
         1 compute + ceph
         1 contrail-config+contrail-control+contrail-db
         1 compute+sriov+dpdk
    4. Deploy cluster.
    5. Run OSTF tests
    6. Launch few instances with image TestVM and flavor m1.micro in nova az.
    7. Launch few instances with image TestVM and flavor m1.small.hpgs
       in hpgs az.
    8. Check connection between instances (ping, ssh).
    9. Reboot node compute+sriov+dpdk.
    10. Launch few instances with image TestVM and flavor m1.small.hpgs
        in hpgs az.
    11. Check connection between instances (ping, ssh).

Expected results
################

All steps should pass
