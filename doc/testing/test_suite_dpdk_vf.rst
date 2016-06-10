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
       * enable dpdk
       * enable sriov
       * enable DPDK on VF
    3. Add following nodes:
       * 3 controller + mongo
       * 1 compute + ceph
       * 1 contrail-config+contrail-control+contrail-db
       * 1 compute+sriov+dpdk
    4. Deploy cluster.
    5. Run OSTF tests.


Expected results
################

All steps should pass


Contrail DPDK on VF add compute
-------------------------------


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
       * enable dpdk
       * enable sriov
       * enable DPDK on VF
    3. Add following nodes:
       * 1 controller
       * 1 compute+sriov+dpdk
       * 1 contrail-config+contrail-control+contrail-db
    4. Deploy cluster.
    5. Run OSTF tests.
    6. Check Controller and Contrail nodes status.
    7. Add one node with compute role.
    8. Deploy changes.
    9. Run OSTF tests.


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
       * enable dpdk
       * enable sriov
       * enable DPDK on VF
    3. Add following nodes:
       * 1 controller
       * 1 compute
       * 1 contrail-config+contrail-control+contrail-db
       * 1 compute+sriov+dpdk
    4. Run OSTF tests.
    5. Delete node with compute role.
    6. Deploy changes.
    7. Run OSTF tests.


Expected results
################

All steps should pass


Contrail DPDK on VF add dpdk
----------------------------


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
       * enable dpdk
       * enable sriov
       * enable DPDK on VF
    3. Add following nodes:
       * 1 controller
       * 1 compute+sriov+dpdk
       * 1 contrail-config+contrail-control+contrail-db
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
       * enable dpdk
       * enable sriov
       * enable DPDK on VF
    3. Add following nodes:
       * 1 controller
       * 2 compute+sriov+dpdk
       * 1 contrail-config+contrail-control+contrail-db
    4. Run OSTF tests.
    5. Delete node with compute+dpdk roles.
    6. Deploy changes.
    7. Run OSTF tests.


Expected results
################

All steps should pass


Contrail DPDK on VF add controller
----------------------------------


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
       * enable dpdk
       * enable sriov
       * enable DPDK on VF
    3. Add following nodes:
       * 1 controller
       * 1 compute+sriov+dpdk
       * 1 contrail-config+contrail-control+contrail-db
    4. Run OSTF tests.
    5. Add node with controller role.
    6. Deploy changes.
    7. Run OSTF tests.


Expected results
################

All steps must be completed successfully, without any errors


Contrail DPDK on VF delete controller
-------------------------------------


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
       * enable dpdk
       * enable sriov
       * enable DPDK on VF
    3. Add following nodes:
       * 3 controller
       * 1 compute+sriov+dpdk
       * 1 contrail-config+contrail-control+contrail-db
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
       * enable dpdk
       * enable sriov
       * enable DPDK on VF
    3. Add following nodes:
       * 1 controller
       * 1 compute
       * 1 contrail-config+contrail-control+contrail-db
       * 1 compute+sriov+dpdk
    4. Deploy cluster.
    5. Run OSTF.
    6. Add "contrail-config", "contrail-control", "contrail-db" roles.
    7. Deploy changes.
    8. Run OSTF.


Expected results
################

All steps must be completed successfully, without any errors.


Contrail DPDK on VF connection between instances
------------------------------------------------


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
       * enable dpdk
       * enable sriov
       * enable DPDK on VF
    3. Add following nodes:
       * 1 controller
       * 1 compute + ceph
       * 1 contrail-config+contrail-control+contrail-db
       * 1 compute+sriov+dpdk
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
-----------------------


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
       * enable dpdk
       * enable sriov
       * enable DPDK on VF
    3. Add following nodes:
       * 1 controller
       * 1 compute + ceph
       * 1 contrail-config+contrail-control+contrail-db
       * 1 compute+sriov+dpdk
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


Check connectivity instances to public network without floating ip.
-------------------------------------------------------------------


ID
##

contrail_dpdk_vf_without_fip


Description
###########

Check connectivity instances to public network without floating ip.


Complexity
##########

core


Steps
#####

    1. Create an environment with "Neutron with tunneling segmentation"
       as a network configuration and CEPH storage
    2. Enable and configure Contrail plugin:
       * enable dpdk
       * enable sriov
       * enable DPDK on VF
    3. Add following nodes:
       * 1 controller
       * 1 compute + ceph
       * 1 contrail-config+contrail-control+contrail-db
       * 1 compute+sriov+dpdk
    4. Deploy cluster.
    5. Run OSTF tests
    6. Create private networks net01 with subnet.
    7. Add one  subnet (net01_subnet01: 192.168.101.0/24.
    8. Create Router_01, set gateway and add interface
       to external network.
    9. Log in to Horizon Dashboard.
    10. Create net_01: net01_subnet, 192.168.112.0/24 and attach it to default router.
    11. Launch few instances with image TestVM and flavor m1.small.hpgs
        in hpgs az.
    12. Send ping from instances to 8.8.8.8 or other outside ip.


Expected results
################

Pings should  get a response


Check connectivity instances to public network with floating ip.
----------------------------------------------------------------


ID
##

contrail_dpdk_vf_public


Description
###########

Check connectivity instances to public network with floating ip.


Complexity
##########

core


Steps
#####

    1. Create an environment with "Neutron with tunneling segmentation"
    2. Enable and configure Contrail plugin:
       * enable dpdk
       * enable sriov
       * enable DPDK on VF
    3. Add following nodes:
       * 1 controller
       * 1 compute + ceph
       * 1 contrail-config+contrail-control+contrail-db
       * 1 compute+sriov+dpdk
    4. Deploy cluster.
    5. Run OSTF tests
    6. Create private networks net01 with subnet.
    7. Add one  subnet (net01_subnet01: 192.168.101.0/24.
    8. Create Router_01, set gateway and add interface
       to external network.
    9. Log in to Horizon Dashboard.
    10. Create net_01: net01_subnet, 192.168.112.0/24 and attach it to default router.
    11. Launch few instances with image TestVM and flavor m1.small.hpgs
        in hpgs az. Associate floating ip.
    12. Send ping from instances to 8.8.8.8 or other outside ip.


Expected results
################

Instances have access to an internet.


Create volume and boot instance from it
---------------------------------------


ID
##

contrail_dpdk_vf_volume


Description
###########

Create volume and boot instance from it


Complexity
##########

core


Steps
#####

    1. Create an environment with "Neutron with tunneling segmentation"
       as a network configuration and CEPH storage
    2. Enable and configure Contrail plugin:
       * enable dpdk
       * enable sriov
       * enable DPDK on VF
    3. Add following nodes:
       * 1 controller
       * 1 compute + ceph
       * 1 cinder
       * 1 contrail-config+contrail-control+contrail-db
       * 1 compute+sriov+dpdk
    4. Deploy cluster.
    5. Run OSTF tests.
    6. Create private networks net01 with subnet.
    7. Add one  subnet (net01_subnet01: 192.168.101.0/24.
    8. Create Router_01, set gateway and add interface
       to external network.
    9. Create a new small-size volume from image.
    10. Wait for volume status to become "available".
    11. Launch instance from created volume with flavor m1.small.hpgs
        in hpgs az. Associate floating ip.
    12. Check that instances have "Active" status.
    13. Check connectivity to instances by floating ip(ping).


Expected results
################

Instances should have "Active" status. Pings should get a response.


Instance live migration
-----------------------


ID
##

contrail_dpdk_vf_migration


Description
###########

Instance live migration


Complexity
##########

core


Steps
#####

    1. Create an environment with "Neutron with tunneling segmentation"
       as a network configuration and CEPH storage
    2. Enable and configure Contrail plugin:
       * enable dpdk
       * enable sriov
       * enable DPDK on VF
    3. Add following nodes:
       * 1 controller
       * 1 compute + ceph
       * 1 contrail-config+contrail-control+contrail-db
       * 2 compute+sriov+dpdk
    4. Deploy cluster.
    5. Run OSTF tests.
    6. Create private networks net01 with subnet.
    7. Add one  subnet (net01_subnet01: 192.168.101.0/24.
    8. Create Router_01, set gateway and add interface
       to external network.
    9. Create a new security group.
    10. Create an instance  with new security group, flavor m1.small.hpgs
        in hpgs az.
    11. Assign floating ip.
    12. Check instance connectivity by floating ip.
    13. Find host to migrate.
    14. Migrate instance.
    15. Check instance host.
    16. Check connectivity to migrated instance by floating ip(ping).


Expected results
################

Instances should be migrated. Pings should get a response.
