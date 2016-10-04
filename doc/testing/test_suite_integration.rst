===================
Integration testing
===================


Deploy HA Environment with Contrail
-----------------------------------


ID
##

contrail_ha


Description
###########

Check Contrail deploy on HA environment


Complexity
##########

Core


Steps
#####

    1. Create an environment with "Neutron with tunneling segmentation" as a network configuration and CEPH storage
    2. Enable and configure Contrail plugin
    3. Add 3 nodes with controller role
    4. Add 3 nodes with "compute" and "Ceph-OSD" roles
    5. Add a node with contrail-control role
    6. Add a node with contrail-analytics role
    7. Add a node with contrail-analytics-db role
    8. Deploy cluster with plugin
    9. Run contrail health check tests
    10. Run OSTF tests


Expected results
################

All steps must be completed successfully, without any errors.


Deploy Environment with  HA-Contrail and Base-OS
------------------------------------------------


ID
##

contrail_ha_baseos


Description
###########

Check deploy HA-contrail on an environment with a base-os node


Complexity
##########

Core


Steps
#####

    1. Create an environment with "Neutron with tunneling
       segmentation" as a network configuration
    2. Enable and configure Contrail plugin
    3. Add a node with controller role
    4. Add 2 nodes with "compute" and "Storage-cinder" roles
    5. Add a node with Base-OS role
    6. Add a node with "contrail-control", "contrail-analytics" roles
    7. Add a node with "contrail-analytics","contrail-analytics-db" role
    8. Deploy cluster with plugin
    9. Run contrail health check tests
    10. Run OSTF tests



Expected results
################

All steps must be completed successfully, without any errors.


Deploy Environment with Contrail and Ceilometer
-----------------------------------------------


ID
##

contrail_ceilometer


Description
###########

Check deploy environment with Contrail and Ceilometer


Complexity
##########

Core


Steps
#####

    1. Create an environment with "Neutron with tunneling
       segmentation" as a network configuration and CEPH storage
    2. Enable and configure Contrail plugin
    3. Add a node with "controller" role
    4. Add a node with "controller" + "MongoDB" multirole
    5. Add a node with "controller"+ "ceph-OSD" multiroles
    6. Add a node with "compute" + "ceph-OSD" + "cinder" multiroles
    7. Add a node with "compute" + "ceph-OSD" multiroles
    8. Add a node with "MongoDB" role
    9. Add a node with "contrail-control" role
    10. Add a node with "contrail-analytics-db" and
        "contrail-analytics"  roles
    11. Deploy cluster with plugin
    12. Run contrail health check tests
    13. Run OSTF tests


Expected results
################

All steps must be completed successfully, without any errors.


Deploy Environment with  Contrail and jumbo-frames support
----------------------------------------------------------


ID
##

contrail_jumbo


Description
###########

Check deploy contrail on an environment with jumbo-frames support


Complexity
##########

Core


Steps
#####

    1. Create an environment with "Neutron with tunneling
       segmentation" as a network configuration
    2. Enable and configure Contrail plugin
    3. Add a node with "controller" and "Ceph OSD" roles
    4. Add 2 nodes with "compute" and "Storage-Ceph OSD" roles
    5. Add a node with "contrail-analytics", "contrail-control" roles
    6. Add node with "contrail-analytics-db" role
    7. Configure MTU on network interfaces (Jumbo-frames)
    8. Deploy cluster with plugin
    9. Run contrail health check tests
    10. Run OSTF tests



Expected results
################

All steps must be completed successfully, without any errors.


Deploy Environment with  Contrail and vlan tagging
--------------------------------------------------


ID
##

contrail_vlan


Description
###########

Check deploy contrail on an environment with vlan-tagging


Complexity
##########

Core


Steps
#####

    1. Create an environment with "Neutron with tunneling
       segmentation" as a network configuration
    2. Enable and configure Contrail plugin
    3. Configure VLAN on network interfaces
    4. Add 3 nodes with controller role
    5. Add 2 nodes with "compute" and "Storage-cinder" roles
    6. Add 2 nodes with "contrail-control" role
    7. Add a node with "contrail-analytics" role
    8. Add a node with 'contrail-analytics-db' role
    9. Deploy cluster with plugin
    10. Run contrail health check tests
    11. Run OSTF tests


Expected results
################

All steps must be completed successfully, without any errors.


Deploy Environment with Contrail and bonding
--------------------------------------------


ID
##

contrail_bonding


Description
###########

Check deploy contrail with aggregation of network interfaces


Complexity
##########

Core


Steps
#####

    1. Create an environment with "Neutron with tunneling
       segmentation" as a network configuration
    2. Enable and configure Contrail plugin
    3. Add 3 nodes with controller role
    4. Add 2 nodes with "compute" roles
    5. Add a node with "contrail-control" role
    6. Add a node with "contrail-analytics" role
    7. Add 2 nodes with "contrail-analytics-db" role
    8. Bond network interfaces with balance-rr mode
    9. Deploy cluster with plugin
    10. Run contrail health check tests
    11. Run OSTF tests


Expected results
################

All steps must be completed successfully, without any errors.


Deploy Environment with Controller + Cinder multirole
-----------------------------------------------------


ID
##

contrail_cinder_multirole


Description
###########

Check deploy contrail with Controller + Cinder multirole


Complexity
##########

Core


Steps
#####

    1. Create an environment with "Neutron with tunneling segmentation" as a network configuration
    2. Enable and configure Contrail plugin
    3. Add 3 nodes with "controller" + "storage-cinder" multirole
    4. Add 2 nodes with "compute" role
    5. Add 2 node with "contrail-control", "contrail-analytics" roles
    6. Add a node with 'contrail-analytics-db' role
    7. Deploy cluster with plugin
    8. Run contrail health check tests
    9. Run OSTF tests


Expected results
################

All steps must be completed successfully, without any errors.


Deploy Environment with Controller + Ceph multirole
---------------------------------------------------


ID
##

contrail_ceph_multirole


Description
###########

Check deploy contrail with Controller + Ceph multirole


Complexity
##########

Core


Steps
#####

    1. Create an environment with "Neutron with tunneling segmentation" as a network configuration and CEPH storage
    2. Enable and configure Contrail plugin
    3. Add 3 nodes with "controller" + "Ceph-OSD" multirole
    4. Add 2 nodes with "compute" role
    5. Add a node with "contrail-control" role
    6. Add 2 nodes with 'contrail-analytics-db',
       "contrail-analytics" roles
    7. Add a node with 'contrail-analytics-db' role
    8. Deploy cluster with plugin
    9. Run contrail health check tests
    10. Run OSTF tests


Expected results
################

All steps must be completed successfully, without any errors.


Deploy Environment with Controller + Cinder + Ceph multirole
------------------------------------------------------------


ID
##

contrail_cinder_ceph_multirole


Description
###########

Check deploy contrail with Controller + Cinder + Ceph multirole


Complexity
##########

Core


Steps
#####

    1. Create an environment with "Neutron with tunneling
       segmentation" as a network configuration and CEPH storage
    2. Enable and configure Contrail plugin
    3. Add 1 node with "controller", "storage-cinder",
       and "Ceph-OSD" roles
    4. Add 1 node with "controller" + "storage-cinder" and 1 node
       with "controller" + "Ceph-OSD" multiroles
    5. Add 1 nodes with "compute", "cinder", "ceph-osd" roles
    6. Add 1 nodes with "compute" role
    7. Add a node with "contrail-control" role
    8. Add 2 node with 'contrail-analytics-db',
       "contrail-analytics" roles
    9. Add a node with 'contrail-analytics-db' role
    10. Deploy cluster with plugin
    11. Run contrail health check tests
    12. Run OSTF tests


Expected results
################

All steps must be completed successfully, without any errors.


Check updating core repos with Contrail plugin
----------------------------------------------


ID
##

contrail_update_core_repos


Description
###########

Check updating core repos with Contrail plugin


Complexity
##########

Core


Steps
#####

    1. Deploy cluster with Contrail plugin
    2. Run 'fuel-mirror create -P ubuntu -G mos ubuntu' on the master node
    3. Run 'fuel-mirror apply -P ubuntu -G mos ubuntu --env <env_id> --replace' on the master node
    4. Update repos for all deployed nodes with command
       "fuel --env <env_id> node --node-id 1,2,3,4,5,6,7,9,10 --tasks setup_repositories" on the master node
    5. Run OSTF and check Contrail node status.


Expected results
################

All steps must be completed successfully, without any errors.


Check deploy contrail with sahara
---------------------------------


ID
##

contrail_sahara


Description
###########

Check deploy contrail with sahara


Complexity
##########

Core


Steps
#####

    1. Create an environment with "Neutron with tunneling
       segmentation" as a network configuration and CEPH storage
    2. Enable sahara
    3. Enable and configure Contrail plugin
    4. Add a node with controller role
    5. Add 3 nodes with "compute" and "Ceph-OSD" roles
    6. Add a node with contrail-control role
    7. Add a node with 'contrail-analytics' role
    8. Add a node with 'contrail-analytics-db' role
    9. Deploy cluster with plugin
    10. Run contrail health check tests
    11. Run OSTF tests

Expected results
################

All steps must be completed successfully, without any errors.


Check deploy contrail with murano
---------------------------------


ID
##

contrail_murano


Description
###########

Check deploy contrail with murano


Complexity
##########

Core


Steps
#####

    1. Create an environment with "Neutron with tunneling
       segmentation" as a network configuration
    2. Enable murano
    3. Enable and configure Contrail plugin
    4. Add a node with controller role
    5. Add a node with "compute" and "Storage-cinder" roles
    6. Add a node with "contrail-control" role
    7. Add a node with "contrail-analytics" role
    8. Add a node with "contrail-analytics-db" role
    9. Deploy cluster with plugin
    10. Run contrail health check tests
    11. Run OSTF tests


Expected results
################

All steps must be completed successfully, without any errors.


Check deploy Contrail VMWare with KVM/QEMU
------------------------------------------


ID
##

contrail_vmware_kvm


Description
###########

Check deploy Contrail VMWare with KVM/QEMU


Complexity
##########

advanced


Steps
#####

    1. Connect to a Fuel with preinstalled Contrail plugin.
    2. Create a new environment with following parameters:
       * Compute: KVM/QEMU + vCenter
       * Networking: Neutron with tunneling segmentation
       * Storage: Ceph
       * Additional services: ceilometer
    3. Run script that prepares vmware part for deployment (creates few Distributed
       Switches and spawns virtual machine on each ESXi node)
    4. Configure Contrail plugin settings:
       * dedicated analytics DB
       * Datastore name
       * Datacenter name
       * Uplink for DVS external
       * Uplink for DVS private
       * DVS external
       * DVS internal
       * DVS private
    5. Add nodes with following roles:
       * Controller + mongo
       * 3 Compute + ceph-osd
       * ComputeVMWare
       * 2 contrail-vmware
       * Contrail-analytics + contrail-control
       * Contrail-analytics + contrail-analytics-db
    6. Configure interfaces on nodes.
    7. Configure network settings.
    8. Configure VMware vCenter settings on VMware tab.
    9. Deploy the cluster.
    10. Run OSTF tests.


Expected results
################

Cluster should be deployed and all OSTF test cases should be passed.
