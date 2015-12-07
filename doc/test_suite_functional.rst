==================
Functional testing
==================


Deploy HA Environment with Plugin
---------------------------------


ID
##

deploy_ha_contrail_plugin


Description
###########

Deploy HA Environment with Contrail Plugin


Complexity
##########

advanced


Steps
#####

    1. Log into the Fuel web UI
    2. Press “New OpenStack Environment”
    3. Specify Environment name as test
    4. Set QEMU or KVM as compute
    5. Select 'Neutron with tunneling segmentation' as a network configuration
    6. Set “default” glance and cinder. Do not use any Additional Services
    7. Press “Create”
    8. Open the Settings tab of the Fuel web UI
    9. Select the Contrail plugin checkbox and configure plugin settings
    10. Configure network
    11. Add 3 nodes with “contrail-db”, "contarail-config" and "contrail-control" roles on all nodes
    12. Add 1 node with “Controller” role
    13. Start deploy
    14. Check Controller and Contrail nodes status
    15. Add a node with “Compute” role.
    16. Start deploy
    17. After the end of deploy run OSTF tests
    18. Add 2 nodes with “Controller” role
    19. Add a node with “Compute” role
    20. Add a node with “Cinder” role
    21. Start deploy
    22. After the end of deploy run OSTF tests


Expected results
################

All steps must be completed successfully, without any errors.


Verify HA with assigning public network to all nodes
----------------------------------------------------


ID
##

deploy_ha_with_pub_net_all_nodes


Description
###########

Deploy HA Environment with Contrail Plugin and assign public network to all nodes


Complexity
##########

advanced


Steps
#####

    1. Log into the Fuel web UI
    2. Press “New OpenStack Environment”
    3. Specify Environment name as test
    4. Set QEMU or KVM as compute
    5. Select 'Neutron with tunneling segmentation' as a network configuration
    6. Set “default” glance and cinder
    7. Do not use any additional services
    8. Press “Create”
    9. Open the Settings tab of the Fuel web UI
    10. Select the Contrail plugin checkbox and configure plugin settings
    11. Select "Assign public network to all nodes" checkbox
    12. Configure network
    13. Add 3 nodes with “contrail-db”, "contarail-config" and "contrail-control" roles on all nodes
    14. Add 1 node with “Controller” and 1 node with “Compute” role
    15. Start deploy
    16. Check Controller and Contrail nodes status
    17. Add 1 node with “Controller” and 1 node with “Compute” role
    18. Start deploy
    19. After the end of deploy run OSTF tests


Expected results
################

All steps must be completed successfully, without any errors.


Verify that it's possible to perform control from nodes after deployment procedure
----------------------------------------------------------------------------------


ID
##

control_from_controller_node


Description
###########

Verify that it's possible to perform control from nodes after deployment procedure


Complexity
##########

advanced


Steps
#####

    1. Log into the Fuel web UI
    2. Create “New OpenStack Environment”
    3. Specify Environment name as test
    4. Set QEMU or KVM as compute
    5. Select 'Neutron with tunneling segmentation' as a network configuration
    6. Set “default” glance and cinder
    7. Do not use any Additional Services
    8. Press “Create”
    9. Open the Settings tab of the Fuel web UI
    10. Select the Contrail plugin checkbox and configure plugin settings
    11. Configure network
    12. Add 3 nodes with with “contrail-db”, "contarail-config" and "contrail-control" roles
    13. Add 1 node with “Controller” role and 1 node with “Compute” node
    14. Start deploy
    15. Check Controller and Contrail nodes status
    16. Ssh to Controller node and verify “neutron net-list”


Expected Results
################

All steps must be completed successfully, without any errors.


Check that Contrail Controller node can be added after deploying
----------------------------------------------------------------


ID
##

contrail_plugin_add_contrail_controller_node


Description
###########

Check that Contrail Controller node can be added after deploying


Complexity
##########

advanced


Steps
#####

    1. Log into the Fuel web UI
    2. Press “New OpenStack Environment”
    3. Specify Environment name as test
    4. Set QEMU or KVM as compute
    5. Select 'Neutron with tunneling segmentation' as a network configuration
    6. Set “default” glance and cinder. Do not use any Additional Services
    7. Press “Create”
    8. Open the Settings tab of the Fuel web UI
    9. Select the Contrail plugin checkbox and configure plugin settings
    10. Configure network
    11. Add 1 nodes with “contrail-db”, "contarail-config" and "contrail-control" roles
    12. Add 1 node with “Controller” role and 1 node with “Compute” role and start deploy.
    13. Check Controller, Compute and Contrail node status and start deploy.
    14. After deploying add two Contrail Controller nodes with “contrail-db”, "contarail-config" and "contrail-control" roles
    15. After the end of deploy run OSTF tests


Expected Results
################

All steps must be completed successfully, without any errors.


Verify deploy Contrail Plugin with vlan tagging
-----------------------------------------------


ID

deploy_ha_with_vlan_tagging


Description
###########

Verify deploy Contrail Plugin with vlan tagging


Complexity
##########

advanced


Steps
#####

    1. Log into the Fuel web UI
    2. Press “New OpenStack Environment”
    3. Specify Environment name as test
    4. Set QEMU or KVM as compute
    5. Select 'Neutron with tunneling segmentation' as a network configuration
    6. Set “default” glance and cinder. Do not use any additional services
    7. Press “Create”
    8. Open the Settings tab of the Fuel web UI
    9. Select the Contrail plugin checkbox and configure plugin settings
    10. Configure network
    11. Use VLAN tagging for storage and management section
    12. Add 3 nodes with “contrail-db”, "contarail-config" and "contrail-control" roles on all nodes
    13. Add 2 nodes with “Controller”
    14. Start deploy
    15. Check Controller nodes status
    16. Add 2 nodes with “Compute” role
    17. Start deploy
    18. After the end of deploy run OSTF tests


Expected Results
################

All steps must be completed successfully, without any errors.


Verify deploy cluster with Networking Templates
------------------------------------------------------------------


ID
##

deploy_contrail_plugin_with_networking_templates


Description
###########

Verify deploy cluster with Networking Templates


Complexity
##########

advanced


Steps
#####

    1. Prepare master node with appropriate iso
    2. Get template from github: fuel-docs/examples/network_templates/two_networks.yaml
    3. Create env with 'Neutron with tunneling segmentation' as a network configuration: fuel env create --name n01 --rel 2 --mode ha --network-mode neutron --net-segment-type gre
    4. Create net-group: fuel network-group --create --name everything --cidr 10.109.1.0/24 --gateway 10.109.1.1 --nodegroup 1
    5. Verify it with command: fuel network-group
    6. Set metadate for net-group: fuel network-group --set --network 6 --meta '{"name": "everything", "notation": "cidr", "render_type": null, "map_priority": 2, "configurable": true, "use_gateway": true, "render_addr_mask": "internal", "vlan_start": null, "cidr": "10.109.1.0/24"}'
    7. Change existing template on taken network_template_1.yaml and upload template: fuel --env 1 network-template --upload --dir /root/
    8. Configure network
    9. Add 3 nodes with “contrail-db”, "contarail-config" and "contrail-control" roles on all nodes
    10. Add 1 node with “Controller” role and 1 node with “Compute” role
    11. Start deploy
    12. After the end of deploy run OSTF tests


Expected Results
################

All steps must be completed successfully, without any errors.

