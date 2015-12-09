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
    2. Launch a new instance
    3. Connect to the  instance via VNC (Horizon) and send ping to the second instance
    4. Connect to one of contrail controller hosts, stop the network interfaces connected to private and management networks.Ping should get a response for verifying HA

Expected Results
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


Expected Results
################

Ping should get a response.


Manual change network settings on instance
------------------------------------------


ID
##

incorrect_network_settings_with_contrail


Description
###########

Manual change network settings on instance


Complexity
##########

advanced


Steps
#####

    1. Login as admin to Openstack Horizon UI
    2. Launch 2 new instances
    3. Connect to the  instance via VNC (Horizon) and manually change network settings by setting free IP address from previously set IP range
    4. Connect to the first instance via VNC (Horizon) and ping the second instance


Expected Result
###############

Ping should not get a response.


Enable/disable port to VM
-------------------------


ID
##

enable_disable_port_to_vm


Description
###########

Enable/disable port to VM


Complexity
##########

advanced


Steps
#####

    1. Create net_01
    2. Launch two instance with it
    3. Verify status of instances
    4. Verify that VMs  should communicate between each other. Send icmp ping from vm _1 to vm_2
    5. Disable port of vm_1
    6. Verify that VMs  should not communicate between each other. Send icmp ping from vm _2 to vm_1
    7. Enable port of vm_1
    8. Verify that VMs  should communicate between each other. Send icmp ping from vm _1 to vm_2


Expected Result
###############

All steps must be completed successfully, without any errors.


Check ssh-connection by floating ip for vm after deleting floating ip
---------------------------------------------------------------------


ID
##

ssh_connection_after_deleting_floating_ip


Description
###########

Check ssh-connection by floating ip for vm after deleting floating ip


Complexity
##########

advanced


Steps
#####

    1. Create network net01, subnet net01__subnet with CIDR 10.1.1.0/24
    2. Create new security group sec_group1
    3. Add Ingress rule for TCP protocol to sec_group1
    4. Boot vm1 net01 with sec_group1
    5. Associate floating IP for vm1
    6. Go to vm1 with ssh and floating IP
    7. Without stopping ssh-connection disassociate floating ip from vm
    8. Check that connection is stopped
    9. Try to go to vm1 with ssh and floating IP
    10. Check that connection is unreacheable


Expected Results
################

All steps must be completed successfully, without any errors.


Check can not deploy Contrail cluster with  ‘contrail_db’ only
--------------------------------------------------------------


ID
##

cannot_deploy_only_contrail_db 


Description
###########

Check can not deploy Contrail cluster with  ‘contrail_db’ only


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
    11. Configure network
    12. Add 1 nodes with “contrail-db” role
    13. Add 1 node with “Controller” and 1 node with “Compute” role
    14. Start deploy


Expected Results
################

Deploy must failed


Check can not deploy Contrail cluster with  ‘contrail_config’ only
------------------------------------------------------------------


ID
##

cannot_deploy_only_contrail_config 


Description
###########

Check can not deploy Contrail cluster with  ‘contrail_config’ only


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
    11. Configure network
    12. Add 1 nodes with “contrail-config” role
    13. Add 1 node with “Controller” and 1 node with “Compute” role
    14. Start deploy


Expected Results
################

Deploy must failed


Check can not deploy Contrail cluster with  ‘contrail_control’ only
-------------------------------------------------------------------


ID
##

cannot_deploy_only_contrail_control 


Description
###########

Check can not deploy Contrail cluster with  ‘contrail_control’ only


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
    11. Configure network
    12. Add 1 nodes with “contrail-control” role
    13. Add 1 node with “Controller” and 1 node with “Compute” role
    14. Start deploy


Expected Results
################

Deploy must failed

