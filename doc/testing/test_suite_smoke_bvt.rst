===============
Smoke/BVT tests
===============


Smoke test
----------


ID
##

contrail_smoke


Description
###########

Deploy a cluster with Contrail Plugin.


Complexity
##########

core


Steps
#####

    1. Create environment with "Neutron with tunneling segmentation" as a network configuration.
    2. Activate and configure the Contrail plugin.
    3. Add a node with contrail-config, contrail-control, contrail-db roles.
    4. Add a node with controller role.
    5. Add a node with compute role.
    6. Deploy cluster with plugin.


Expected results
################

All steps must be completed successfully, without any errors.


BVT test
--------


ID
##

contrail_bvt


Description
###########

BVT test for contrail plugin. Deploy cluster with a controller, a compute, a contrail-config, a contrail-control, a contrail-db roles and install contrail plugin.


Complexity
##########

core


Steps
#####

    1. Create an environment with "Neutron with tunneling
       segmentation" as a network configuration
    2. Enable Contrail plugin
    3. Enable dedicated analytics DB
    4. Add a node with contrail-config role
    5. Add a node with contrail-control role
    6. Add 3 nodes with contrail-db role
    7. Add a node with contrail-analytics-db role.
    8. Add a node with contrail-analytics role
    9. Add a node with with controller role
    10. Add a node with compute + cinder role
    11. Deploy cluster with plugin
    12. Run contrail health check tests
    13. Run OSTF tests

Expected results
################

All steps must be completed successfully, without any errors.
