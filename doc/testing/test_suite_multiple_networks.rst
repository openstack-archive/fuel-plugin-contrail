=================
Multiple Networks
=================


Contrail HA Multiple Networks
-----------------------------


ID
##

contrail_ha_multiple_nodegroups


Description
###########

Deploy HA environment with Neutron GRE and 2 nodegroupst


Complexity
##########

advanced


Steps
#####

    1. Revert snapshot with ready master node
    2. Install contrail plugin
    3. Bootstrap slaves from default nodegroup
    4. Create cluster with Neutron GRE and custom nodegroups
    5. Activate plugin and configure plugins setings
    6. Remove 2nd custom nodegroup which is added automatically
    7. Bootstrap slave nodes from custom nodegroup
    8. Download network configuration
    9. Update network.json  with customized ip ranges
    10. Put new json on master node and update network data
    11. Verify that new IP ranges are applied for network config
    12. Add following nodes to default nodegroup:
        * 3 controller+mongo+ceph
    13. Add following nodes to custom nodegroup:
        * 1 compute
        * 1 contrail-config+contrail-control+contrail-db
    14. Deploy cluster
    15. Run network verification
    16. Verify that excluded ip is not used for nodes or VIP
    17. Run health checks (OSTF)


Expected results
################
All steps must be completed successfully, without any errors