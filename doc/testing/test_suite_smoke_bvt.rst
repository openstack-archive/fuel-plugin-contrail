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
    3. Add a node with contrail-controller role.
    4. Add a node with controller role.
    5. Add a node with compute role.
    6. Add a node with contrail-analytics + contrail-analytics-db roles
    7. Deploy cluster with plugin.


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
    3. Add a 2 nodes with contrail-controller role
    4. Add a 2 nodes with contrail-analytics-db role.
    5. Add a node with contrail-analytics + contrail-analytics-db roles
    6. Add a node with contrail-analytics + contrail-controller roles
    7. Add a node with contrail-analytics role
    8. Add a node with controller role
    9. Add a node with compute + cinder roles
    10. Deploy cluster with plugin
    11. Run contrail health check tests
    12. Run OSTF tests

Expected results
################

All steps must be completed successfully, without any errors.


Contrail VMWare smoke
---------------------


ID
##

contrail_vmware_smoke


Description
###########

Deploy a cluster with Contrail Plugin and VMWare


Complexity
##########

advanced


Steps
#####

    1. Connect to a Fuel with preinstalled Contrail plugin.
    2. Create a new environment with following parameters:
       * Compute: vCenter
       * Networking: Neutron with tunneling segmentation
       * Storage: default
       * Additional services: default
    3. Run script that prepares vmware part for deployment (creates few Distributed
       Switches and spawns virtual machine on each ESXi node)
    4. Configure Contrail plugin settings:
       * Datastore name
       * Datacenter name
       * Uplink for DVS external
       * Uplink for DVS private
       * DVS external
       * DVS internal
       * DVS private
    5. Add nodes with following roles:
       * Controller
       * ComputeVMWare
       * Compute
       * Contrail-controller
       * Contrail-analytics + contrail-analytics-db
       * Contrail-vmware
    6. Configure interfaces on nodes.
    7. Configure network settings.
    8. Configure VMware vCenter settings on VMware tab.
    9. Deploy the cluster.
    10. Run OSTF tests.


Expected results
################

Cluster should be deployed and all OSTF test cases should be passed.
