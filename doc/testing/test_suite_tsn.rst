===
TSN
===


Contrail TSN
------------


ID
##

contrail_tsn


Description
###########

Check Contrail deploy on HA environment


Complexity
##########

advanced


Steps
#####

    1. Connect to a Fuel with preinstalled Contrail plugin.
    2. Create a new environment with following parameters:
       * Compute: QEMU
       * Networking: Neutron with tunneling segmentation
       * Storage: Ceph
       * Additional services: ceilometer
    3. Configure Contrail plugin settings:
       * enable and configure ToR agents
    4. Add nodes with following roles:
       * 3 Controller
       * 1 TSN
       * 2 Compute + Ceph
       * 1 contrail-control
       * 1 contrail-analytics + contrail-analytics-db
    5. Configure interfaces on nodes.
    6. Configure network settings.
    7. Deploy the cluster.
    8. Run OSTF tests.
    9. Verify that TLS certificate should be  generated for TSN and TOR.


Expected results
################

All steps must be completed successfully, without any errors


Contrail TSN HA
---------------


ID
##

contrail_tsn_ha


Description
###########

Check Contrail deploy with TSN HA mode


Complexity
##########

advanced


Steps
#####

    1. Connect to a Fuel with preinstalled Contrail plugin.
    2. Create a new environment with following parameters:
       * Compute: QEMU
       * Networking: Neutron with tunneling segmentation
    3. Configure Contrail plugin settings:
       * enable and configure ToR agents
    4. Add nodes with following roles:
       * 1 Controller
       * 2 TSN
       * 1 Compute
       * 1 contrail-control + contrail-analytics
       * 1 contrail-analytics + contrail-analytics-db
    5. Configure interfaces on nodes.
    6. Configure network settings.
    7. Deploy the cluster.
    8. Run OSTF tests.
    9. Add TOR switch and configure interfaces via Contrail UI.
    10. Check that ToR agent is active.
    11. Reboot TSN nodes.
    12. Check that ToR agents is active after reboot.


Expected results
################

All steps must be completed successfully, without any errors


Contrail TSN Interaction
------------------------


ID
##

contrail_tsn_interaction


Description
###########

Check that the TOR agent sends OVSDB tables onto the TOR switch.


Complexity
##########

advanced


Steps
#####
    1. Setup Contrail TSN HA.
    2. Launch few instances.
    3. Add ips and macs of instances to TOR interface via Contrail UI.
    4. Check that associated instance ports is displayed in the local unicast table on TOR switch.
       Run command 'ovs-vsctl show'.


Expected results
################

Cluster should be deployed and OSTF test cases should be passed.
All associated instance ports is displayed in the local unicast table on TOR switch.


Contrail TSN add TSN
--------------------


ID
##

contrail_add_tsn


Description
###########

Verify that TSN node can be added after deploy


Complexity
##########

advanced


Steps
#####

    1. Connect to a Fuel with preinstalled Contrail plugin.
    2. Create a new environment with following parameters:
       * Compute: QEMU
       * Networking: Neutron with tunneling segmentation
       * Storage: default
       * Additional services: default
    3. Configure Contrail plugin settings:
       * enable and configure ToR agents
    4. Add nodes with following roles:
       * 1 Controller
       * 1 TSN
       * 1 Compute
       * 1 contrail-config + contrail-analytics
       * 1 contrail-analytics + contrail-analytics-db
    5. Configure interfaces on nodes.
    6. Configure network settings.
    7. Deploy the cluster.
    8. Run OSTF tests.
    9. Add TSN node.
    10. Redeploy cluster.
    11. Run OSTF tests.


Expected results
################

Cluster should be deployed and OSTF test cases should be passed.


Contrail TSN remove TSN
-----------------------


ID
##

contrail_delete_tsn


Description
###########

Verify that TSN node can be deleted after deploy


Complexity
##########

advanced


Steps
#####

    1. Connect to a Fuel with preinstalled Contrail plugin.
    2. Create a new environment with following parameters:
       * Compute: QEMU
       * Networking: Neutron with tunneling segmentation
       * Storage: Ceph
       * Additional services: default
    3. Configure Contrail plugin settings:
       * enable and configure ToR agents
    4. Add nodes with following roles:
       * 1 Controller + ceph-osd
       * 2 TSN
       * 1 Compute + cinder
       * 1 contrail-control + contrail-analytics
       * 1 contrail-analytics-db
    5. Configure interfaces on nodes.
    6. Configure network settings.
    7. Deploy the cluster.
    8. Run OSTF tests.
    9. Add TSN node.
    10. Redeploy cluster.
    11. Run OSTF tests.


Expected results
################

Cluster should be deployed and OSTF test cases should be passed.
