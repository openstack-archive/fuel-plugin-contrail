===
TSN
===


Contrail HA TSN
----------------


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
       * Storage: ceph
       * Additional services: ceilometer
    3. Add nodes with following roles:
       * 3 Controller + mongo
       * 1 TSN
       * 3 Compute + Ceph
       * 1 Contrail-config + contrail-control + contrail-db
    4. Configure interfaces on nodes.
    5. Configure network settings.
    6. Configure Contrail plugin settings:
       * enable ToR agents
       * enable ToR agents ssl mode
    7. Deploy the cluster.
    8. Run OSTF tests.
    9. Check that ToR agent is active.


Expected results
################

All steps must be completed successfully, without any errors


Contrail TSN add controller
---------------------------


ID
##

contrail_tsn_add_controller


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
       * enable ToR agents
       * enable ToR agents ssl mode
    3. Add following nodes:
       * 1 controller
       * 1 TSN
       * 1 compute
       * 1 contrail-config+contrail-control+contrail-db
    4. Run OSTF tests.
    5. Add node with controller role.
    6. Deploy changes.
    7. Run OSTF tests.


Expected results
################

All steps must be completed successfully, without any errors


Contrail TSN on VF delete controller
------------------------------------


ID
##

contrail_tsn_delete_controller


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
       * enable ToR agents
       * enable ToR agents ssl mode
    3. Add following nodes:
       * 3 controller
       * 1 TSN
       * 1 compute
       * 1 contrail-config+contrail-control+contrail-db
    4. Run OSTF tests.
    5. Delete node with controller role.
    6. Deploy changes.
    7. Run OSTF tests.


Expected results
################

Cluster should be deployed and OSTF test cases should be passed.


Contrail reboot TSN
-------------------


ID
##

contrail_tsn_reboot_tsn


Description
###########

Check TOR agents after reboot TSN node


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
    3. Add nodes with following roles:
       * 1 Controller
       * 1 TSN
       * 1 Compute
       * 1 Contrail-config + contrail-control + contrail-db
    4. Configure interfaces on nodes.
    5. Configure network settings.
    6. Configure Contrail plugin settings.
    7. Deploy the cluster.
    8. Run OSTF tests.
    9. Rebbot TSN node.
    10. Check that ToR agents is active after reboot.


Expected results
################

Cluster should be deployed and OSTF test cases should be passed.
ToR agents should be active after reboot.


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

    1. Connect to a Fuel with preinstalled Contrail plugin.
    2. Create a new environment with following parameters:
       * Compute: QEMU
       * Networking: Neutron with tunneling segmentation
       * Storage: default
       * Additional services: default
    3. Add nodes with following roles:
       * 1 Controller
       * 1 TSN
       * 1 Compute
       * 1 Contrail-config + contrail-control + contrail-db
    4. Configure interfaces on nodes.
    5. Configure network settings.
    6. Configure Contrail plugin settings:
       * enable ToR agents
    7. Deploy the cluster.
    8. Run OSTF tests.
    9. Launch few instances.
    10. Check that assosiated instance ports is displayd in the local unicast table on TOR switch.
        Run command 'vtep-ctl list Physical_Port'


Expected results
################

Cluster should be deployed and OSTF test cases should be passed.
All assosiated instance ports is displayd in the local unicast table on TOR switch.


Contrail TSN SSl
----------------


ID
##

contrail_tsn_tls


Description
###########

Check that TLS certificate is generated for TSN and TOR


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
    3. Add nodes with following roles:
       * 1 Controller
       * 1 TSN
       * 1 Contrail-config + contrail-control + contrail-db
    4. Configure interfaces on nodes.
    5. Configure network settings.
    6. Configure Contrail plugin settings:
       * enable ToR agents
       * enable ToR agents ssl mode
    7. Deploy the cluster.
    8. Run OSTF tests.


Expected results
################

Cluster should be deployed and OSTF test cases should be passed.
TLS certificate should be  generated for TSN and TOR


Contrail TOR add Compute
------------------------


ID
##

contrail_tsn_add_compute


Description
###########

Check that information of instances ports are updated after creating them in the
new compute node.


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
    3. Add nodes with following roles:
       * 1 Controller
       * 1 TSN
       * 1 Compute
       * 1 Contrail-config + contrail-control + contrail-db
    4. Configure interfaces on nodes.
    5. Configure network settings.
    6. Configure Contrail plugin settings:
       * enable ToR agents
       * enable ToR agents ssl mode
    7. Deploy the cluster.
    8. Run OSTF tests.
    9. Add Compute node.
    10. Create few instances.
    11. Check that information of instances ports are updated after creating
        them in the new compute node.


Expected results
################

Cluster should be deployed and OSTF test cases should be passed.
Information of instances ports are updated after creating them in the
new compute node.


Contrail TOR remove Compute
---------------------------


ID
##

contrail_tsn_remove_compute


Description
###########

Check that information of instances ports are updated after removing compute node.


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
    3. Add nodes with following roles:
       * 1 Controller
       * 1 TSN
       * 2 Compute
       * 1 Contrail-config + contrail-control + contrail-db
    4. Configure interfaces on nodes.
    5. Configure network settings.
    6. Configure Contrail plugin settings:
       * enable ToR agents
       * enable ToR agents ssl mode
    7. Deploy the cluster.
    8. Run OSTF tests.
    9. Create few instances on compute hosts.
    10. Remove Compute node.
    11. Redeploy cluster.
    12. Check that information of instances ports are updated after removing compute node.


Expected results
################

Cluster should be deployed and OSTF test cases should be passed.
Information of instances ports should be updated after removing compute node.
