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
        * enable DPDK on VF
        * enable dedicated analytics DB
    3. Add following nodes:
        * 3 controller + mongo
        * 3 compute + ceph
        * 1 contrail-config+contrail-control+contrail-db
        * 1 compute+dpdk
        * 1 contrail-analytics+contrail-analytics-db
        * 1 contrail-db
    4. Enable sriov on interfaces.
    5. Deploy cluster.
    6. Run OSTF tests.
    7. Run contrail health check tests


Expected results
################

All steps should pass
