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
       * 1 contrail-analytics
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


NOOP
----