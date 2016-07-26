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
       * 1 contrail-db+contrail-analytics
       * 1 contrail-db
    4. Deploy cluster.
    5. Run OSTF tests.
    6. Run contrail health check tests


Expected results
################

All steps should pass


NOOP
----
