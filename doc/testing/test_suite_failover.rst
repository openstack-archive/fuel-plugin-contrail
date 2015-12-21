================
Failover testing
================


Check Contrail HA using network problems
----------------------------------------


ID
##

contrail_ha_with_network_problems


Description
###########

Check Contrail HA using network problems


Complexity
##########

advanced


Steps
#####

    1. Login as admin to Openstack Horizon UI
    2. Launch 2 new instances
    3. Connect to the first instance via VNC (Horizon) and send ping to the second instance
    4. Connect to a contrail controller host, stop the network interfaces connected to private and management networks.


Expected results
################

Ping should get a response for verifying HA


Check Contrail HA using node problems
-------------------------------------


ID
##

contrail_ha_with_node_problems


Description
###########

Check Contrail HA using node problems


Complexity
##########

advanced


Steps
#####

    1. Login as admin to Openstack Horizon UI
    2. Launch 2 new instances
    3. Connect to the first instance via VNC (Horizon) and ping the second instance
    4. With a pause of 5-10 minutes turn off and turn on each of Contrail Nodes


Expected results
################

Ping should get a response.


Check can not deploy Contrail cluster with  "contrail_db" only
--------------------------------------------------------------


ID
##

cannot_deploy_only_contrail_db


Description
###########

Check can not deploy Contrail cluster with  "contrail_db" only


Complexity
##########

advanced


Steps
#####

    1. Log into the Fuel web UI
    2. Press "New OpenStack Environment"
    3. Specify Environment name as test
    4. Set QEMU or KVM as compute
    5. Select "Neutron with tunneling segmentation" as a network configuration
    6. Set "default" glance and cinder
    7. Do not use any additional services
    8. Press "Create"
    9. Open the Settings tab of the Fuel web UI
    10. Select the Contrail plugin checkbox and configure plugin settings
    11. Configure network
    12. Add 1 nodes with "contrail-db" role
    13. Add 1 node with "Controller" and 1 node with "Compute" role
    14. Start deploy


Expected results
################

Deploy must failed


Check can not deploy Contrail cluster with  "contrail_config" only
------------------------------------------------------------------


ID
##

cannot_deploy_only_contrail_config


Description
###########

Check can not deploy Contrail cluster with  "contrail_config" only


Complexity
##########

advanced


Steps
#####

    1. Log into the Fuel web UI
    2. Press "New OpenStack Environment"
    3. Specify Environment name as test
    4. Set QEMU or KVM as compute
    5. Select "Neutron with tunneling segmentation" as a network configuration
    6. Set "default" glance and cinder
    7. Do not use any additional services
    8. Press "Create"
    9. Open the Settings tab of the Fuel web UI
    10. Select the Contrail plugin checkbox and configure plugin settings
    11. Configure network
    12. Add 1 nodes with "contrail-config" role
    13. Add 1 node with "Controller" and 1 node with "Compute" role
    14. Start deploy


Expected results
################

Deploy must failed


Check can not deploy Contrail cluster with  "contrail_control" only
-------------------------------------------------------------------


ID
##

cannot_deploy_only_contrail_control


Description
###########

Check can not deploy Contrail cluster with  "contrail_control" only


Complexity
##########

advanced


Steps
#####

    1. Log into the Fuel web UI
    2. Press "New OpenStack Environment"
    3. Specify Environment name as test
    4. Set QEMU or KVM as compute
    5. Select "Neutron with tunneling segmentation" as a network configuration
    6. Set "default" glance and cinder
    7. Do not use any additional services
    8. Press "Create"
    9. Open the Settings tab of the Fuel web UI
    10. Select the Contrail plugin checkbox and configure plugin settings
    11. Configure network
    12. Add 1 nodes with "contrail-control" role
    13. Add 1 node with "Controller" and 1 node with "Compute" role
    14. Start deploy


Expected results
################

Deploy must failed

