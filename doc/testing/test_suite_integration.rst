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

    1. Create an environment with "Neutron with tunneling segmentation" as a network configuration
    2. Enable and configure Contrail plugin
    3. Add 3 nodes with controller role
    4. Add 2 nodes with "compute+Cinder" roles
    5. Add a node with contrail-config role
    6. Add a node with contrail-control role
    7. Add a node with contrail-db role
    8. Deploy cluster with plugin
    9. Run OSTF tests


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

    1. Create an environment with "Neutron with tunneling segmentation" as a network configuration
    2. Enable and configure Contrail plugin
    3. Add a node with controller role
    4. Add 2 nodes with "compute" and "Storage-cinder" roles
    5. Add a node with Base-OS role
    6. Add 3 nodes with "contrail-config", "contrail-control" and "contrail-db" roles
    7. Deploy cluster with plugin
    8. Run OSTF tests


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

    1. Create an environment with "Neutron with tunneling segmentation" as a network configuration and CEPH storage
    2. Enable and configure Contrail plugin
    3. Add 3 nodes with controller role
    4. Add 2 nodes with "compute" and "Ceph-OSD" roles
    5. Add a node with "MongoDB" role
    6. Add a node with "contrail-config", "contrail-control" and "contrail-db" roles
    7. Deploy cluster with plugin
    8. Run OSTF tests


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

    1. Create an environment with "Neutron with tunneling segmentation" as a network configuration
    2. Enable and configure Contrail plugin
    3. Add a node with controller role
    4. Add 2 nodes with "compute" and "Storage-cinder" roles
    5. Add a node with "contrail-config", "contrail-control" and "contrail-db" roles
    6. Add 2 nodes with "contrail-config", "contrail-control" roles
    7. Configure MTU on network interfaces (Jumbo-frames)
    8. Deploy cluster with plugin
    9. Run OSTF tests


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

    1. Create an environment with "Neutron with tunneling segmentation" as a network configuration
    2. Enable and configure Contrail plugin
    3. Add 3 nodes with controller role
    4. Add 2 nodes with "compute" and "Storage-cinder" roles
    5. Add a node with "contrail-config" and "contrail-db" roles
    6. Add a node with "contrail-db", "contrail-control" roles
    7. Add a node with "contrail-db" role
    8. Configure VLAN on network interfaces
    9. Deploy cluster with plugin
    10. Run OSTF tests


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

    1. Create an environment with "Neutron with tunneling segmentation" as a network configuration
    2. Enable and configure Contrail plugin
    3. Add 3 nodes with "controller" role
    4. Add 2 nodes with "compute" roles
    5. Add 3 nodes with "contrail-config", "contrail-control" and "contrail-db" roles
    6. Bond network interfaces with balance-rr mode
    7. Deploy cluster with plugin
    8. Run OSTF tests


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
    4. Add 1 node with "compute" role
    5. Add 2 nodes with "contrail-config", "contrail-control" and "contrail-db" roles
    6. Deploy cluster with plugin
    8. Run OSTF tests


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
    5. Add 1 node with "contrail-config", "contrail-control" and "contrail-db" roles
    6. Deploy cluster with plugin
    8. Run OSTF tests


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

    1. Create an environment with "Neutron with tunneling segmentation" as a network configuration and CEPH storage
    2. Enable and configure Contrail plugin
    3. Add 1 node with "controller" + "storage-cinder" + "Ceph-OSD" multirole
    4. Add 1 node with "controller" + "storage-cinder" and 1 node with "controller" + "Ceph-OSD" multiroles
    4. Add 2 nodes with "compute" role
    5. Add 3 nodes with "contrail-config", "contrail-control" and "contrail-db" roles
    6. Deploy cluster with plugin
    8. Run OSTF tests


Expected results
################

All steps must be completed successfully, without any errors.


Deploy cluster with Contrail plugin and network template
--------------------------------------------------------


ID
##

contrail_net_template


Description
###########

Deploy cluster with Contrail plugin and network template


Complexity
##########

Core


Steps
#####

    1. Configure interfaces
    2. Next we need to set gateway for private network with Fuel CLI:
       * Login with ssh to Fuel master node.
       * List existing network-groups
       fuel network-group --env 1
    3. Remove and create again network-group private to set a gateway
       fuel network-group --delete --network 5
       fuel network-group --create --name private --cidr 10.109.3.0/24 --gateway 10.109.3.1 --nodegroup 1
    4. Set the render_addr_mask parameter to internal for this network by typing:
       fuel network-group --set --network 6 --meta '{"name": "private", "notation": "cidr", "render_type": null, "map_priority": 2, "configurable": true, "use_gateway": true, "render_addr_mask": "internal", "vlan_start": null, "cidr": "10.109.3.0/24"}'
    5. Save sample :download:
       network template<examples/network_template_1.yaml>
    6. Upload the network template by typing:
       fuel --env 1 network-template --upload --dir /root/
    7. Start deploy, pressing "Deploy changes" button.

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
    2. Run “fuel-createmirror -M” on the master node
    3. Update repos for all deployed nodes with command "fuel --env <ENV_ID> node --node-id <NODE_ID1>, <NODE_ID2>, <NODE_ID_N> --tasks upload_core_repos" on the master node


Expected results
################

All steps must be completed successfully, without any errors.
