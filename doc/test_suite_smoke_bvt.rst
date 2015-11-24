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

Deploy a cluster with Contrail Plugin


Complexity
##########

smoke


Steps
#####

    1. Create environment with "Neutron with GRE segmentation" as a network configuration
    2. Press "Settings" tab, select the Contrail plugin checkbox and configure plugin settings
    3. Add a node with contrail-config, contrail-control, contrail-db roles
    4. Add a node with controller role
    5. Deploy cluster with plugin


BVT test
--------


ID
##

contrail_bvt


Description
###########

BVT test for contrail plugin. Deploy cluster with a controller, a compute, a contrail-config, a contrail-control, a contrail-db roles and install contrail plugin


Complexity
##########

smoke


Steps
#####

    1. Create environment with "Neutron with GRE segmentation" as a network configuration
    2. Add a node with contrail-config role
    3. Add a node with contrail-control role
    4. Add a node with contrail-db role
    5. Add a node with controller role
    6. Add a node with "compute" and "cinder" roles
    7. Enable and configure Contrail plugin
    8. Deploy cluster with plugin
    9. Run OSTF tests

