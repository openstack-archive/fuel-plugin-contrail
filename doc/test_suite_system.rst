==============
System testing
==============


Check connectivity between instances in a single private network
----------------------------------------------------------------


ID
##

contrail_vm_connection_in_single_net


Description
###########

Check connectivity between instances placed in a single private network and hosted on different nodes via Contrail network


Complexity
##########

Advanced


Steps
#####

    1. Login as admin to Openstack Horizon UI
    2. Create a private network
    3. Launch 2 new instances in the network. Make sure that VMs were scheduled to different compute nodes. Otherwise, migrate vm2 to another compute
    4. Check ping connectivity between instances
    5. Connect to Compute Node via SSH and check the VM's connections with flow's command (flow -l)
    6. Verify on Contrail controller WebUI that network is there and VMs are attached to it


Expected results
################

Ping should get a response, VMs are present  in Contrail controller WebUI


Check no connectivity between VMs in different tenants via Contrail network
---------------------------------------------------------------------------


ID
##

contrail_vm_connection_in_different_tenants


Description
###########

Check no connectivity between VMs in different tenants via Contrail network


Complexity
##########

Advanced


Steps
#####

    1. Login as admin to Openstack Horizon UI
    2. Create 2 new tenants (the tenants under test must have intersecting or the same IP address spaces and the must be no policy enabled, which allows the traffic between tenants)
    3. Launch 2 new instance in different tenants
    4. Check ping connectivity between instances
    5. Connect to Compute Node via SSH and check the VM's connections
    6. Verify on Contrail controller WebUI that networks are there and VMs are attached to different networks.


Expected results
################

Ping should not get a response, VM's connections should be in the different ethernet device, VMs are present  in Contrail controller WebUI


Check connectivity via external Contrail network without floating IP
--------------------------------------------------------------------


ID
##

contrail_vm_connection_without_floating_ip


Description
###########

Check connectivity VMs with external network without floating IP via Contrail network


Complexity
##########

Advanced


Steps
#####

    1. Login as admin to Openstack Horizon UI
    2. Launch a new instance
    3. Send ping to external IP (example 8.8.8.8)
    4. Ping an IP address of lab host which is a gateway for vSRX
    5. Verify on Contrail controller WebUI that network is there and VMs are attached to it


Expected results
################

Ping should get a response, VMs are present  in Contrail controller WebUI


Create a new network via Contrail WebUI
---------------------------------------


ID
##

create_new_network_via_contrail


Description
###########

Create a new network via Contrail WebUI


Complexity
##########

Advanced


Steps
#####

    1. Login as admin to Contrail WebUI
    2. Create a new network
    3. Login as admin to Openstack Horizon UI
    4. Launch 2 new instance in the network
    5. Check ping connectivity between instances
    6. Verify on Contrail controller WebUI that network is there and VMs are attached to it


Expected results
################

The network is created, Ping should get a response, VMs are present  in Contrail controller WebUI


Check connectivity via external Contrail network with floating IP
-----------------------------------------------------------------


ID
##

contrail_vm_connection_with_floating_ip


Description
###########

Check connectivity VMs with external network with floating IP via Contrail network


Complexity
##########

Advanced


Steps
#####

    1. Login to Openstack Horizon UI
    2. Launch a new instance
    3. Login on Contrail controller WebUI and verify that VMs are attached to it
    4. Assign a Floating IP to the VM via Contrail controller WebUI
    5. Connect to the  instance via VNC (Horizon) and send ping to 8.8.8.8 or any other IP outside the cloud
    6. Allow ping in Security group section via Contrail WebUI
    7. Send ping from external (HOST) machine to Floating IP (emulate external network)


Expected results
################

Floating IP is added, Ping should get a response, VMs are present  in Contrail controller WebUI


Create and terminate networks and verify it in Contrail UI
----------------------------------------------------------


ID
##

create_networks


Description
###########

Create and terminate networks and verify it in Contrail UI


Complexity
##########

Advanced


Steps
#####

    1. Add private 2 networks
    2. Verify that networks are present in Contrail UI
    3. Remove a private network.
    4. Verify that the network is absent in Contrail UI
    5. Add private a network.
    6. Verify that all networks are present in Contrail UI


Expected results
################

All steps must be completed successfully, without any errors.


Verify traffic flow in jumbo-frames-enabled network
---------------------------------------------------


ID
##

traffic_flow_in_jumbo-frames-enabled_network


Description
###########

Verify traffic flow in jumbo-frames-enabled network


Complexity
##########

Advanced


Steps
#####

    1. Login as admin to Openstack Horizon UI
    2. Launch 2 new instances with default parameters
    3. Check ping connectivity between instances
    4. Connect to Compute Node via SSH and check the VM's connections with flow's command (flow -l)
    5. Verify on Contrail controller WebUI that network is there and VMs are attached to it


Expected results
################

All steps must be completed successfully, without any errors.


Test new security group
-----------------------


ID
##

launch_instances_with_new_security_group


Description
###########

Launch instance with new security group and check connection after deleting ICMP and TCP rules


Complexity
##########

Advanced


Steps
#####

    1. Login as admin to Openstack Horizon UI
    2. Launch 2 instances
    3. Verify that instances are present in Contrail UI
    4. Create a security group to allow TCP traffic port 22.
    5. Create a security group to allow ICMP traffic.
    6. Apply the security groups to the instances in different variation


Expected results
################

Connectivity must comply with the rules


Check connectivity on different nodes and different private networks
--------------------------------------------------------------------


ID
##

contrail_vm_connect_on_diff_nodes


Description
###########

Check connectivity between instances placed in different private networks and hosted on different nodes


Complexity
##########

Advanced


Steps
#####

    1. Login as admin to Openstack Horizon UI
    2. Create 2 networks
    3. Launch 2 instances in different network. Make sure that VMs were scheduled to different compute nodes. Otherwise, migrate an instance to another compute
    4. Connect the networks (create a router via horizon)
    5. Check ping connectivity between instances
    6. Remove the router
    7. Connect to Compute node via SSH and check the VM's connections with flow's command (flow -l)
    8. Ping not get response
    9. Login to Contrail WebUI
    10. Connect the networks via Contrail Network Policies
    11. Check ping connectivity between instances
    12. Connect to Compute node via SSH and check the VM's connections with flow's command (flow -l)Ping should get a response
    13. Verify on Contrail controller WebUI that networks is there and VMs are attached to it


Expected results
################

Ping should get a response, VMs are present  in Contrail controller WebUI


Check connectivity on a single node and different private networks
------------------------------------------------------------------


ID
##

contrail_vm_connect_on_single_node


Description
###########

Check connectivity between instances placed in different private networks and hosted on a single node


Complexity
##########

Advanced


Steps
#####

        1. Login as admin to Openstack Horizon UI
    2. Create 2 networks
    3. Launch 2 instances in different network. Make sure that VMs were placed on one compute nodes.
    4. Connect the networks (create a router via horizon)
    5. Check ping connectivity between instances
    6. Remove the router
    7. Connect to Compute node via SSH and check the VM's connections with flow's command (flow -l)
    8. Ping not get response
    9. Login to Contrail WebUI
    10. Connect the networks via Contrail Network Policies
    11. Check ping connectivity between instances
    12. Connect to Compute node via SSH and check the VM's connections with flow's command (flow -l)Ping should get a response
    13. Verify on Contrail controller WebUI that networks is there and VMs are attached to it


Expected results
################

All steps must be completed successfully, without any errors.


Check connectivity on a single node and a single private networks
-----------------------------------------------------------------


ID
##

contrail_vm_connect_on_single_node_single_net


Description
###########

Check connectivity for instances scheduled on a single compute in a single private network


Complexity
##########

Advanced


Steps
#####

    1. Login as admin to Openstack Horizon UI
    2. Create a network
    3. Launch 2 new instances in the network. Make sure that VMs were placed on one compute nodes.
    4. Check ping connectivity between instances
    5. Connect to Compute node via SSH and check the VM's connections with flow's command (flow -l)
    6. Verify on Contrail controller WebUI that network is there and VMs are attached to it


Expected results
################

All steps must be completed successfully, without any errors.


Check ability to a create contrail-specific atrributes heat template
--------------------------------------------------------------------


ID
##

create_stacks_from_heat_template


Description
###########

Check ability to create stacks with contrail-specific atrributes from heat template.


Complexity
##########

Advanced


Steps
#####

    1. Create stack with heat template.
    2. Check that stack was created.


Expected results
################

Stack should be created.


Verify port security for instances
----------------------------------


ID
##

contrail_port_security


Description
###########

Verify that only the associated MAC and IP addresses can communicate on the logical port.


Complexity
##########

advanced


Steps
#####

    1. Login as admin to Openstack Horizon UI
    2. Launch a new instances
    3. Connect to the  instance via VNC (Horizon) and manually change IP address
    4. Check network connectivity (for example ping)
    5. Return IP value on the instance and change MAC address
    6. Check network connectivity (for example ping)


Expected results
################

Ping should not get a response.


Enable/disable port to VM
-------------------------


ID
##

contrail_enable_disable_port_to_vm


Description
###########

Enable/disable port to VM


Complexity
##########

advanced


Steps
#####

    1. Create a network
    2. Launch 2 instance with it
    3. Verify status of instances
    4. Check ping connectivity between instances
    5. Disable port of an instance
    6. Check ping connectivity between instances
    7. Enable port of an instance
    8. Check ping connectivity between instances


Expected results
################

All steps must be completed successfully, without any errors.


Check ssh-connection by floating ip for vm after deleting floating ip
---------------------------------------------------------------------


ID
##

contrail_ssh_connect_after_deleting_floating_ip


Description
###########

Check ssh-connection by floating ip for vm after deleting floating ip


Complexity
##########

Advanced


Steps
#####

    1. Create a network with CIDR 10.1.1.0/24
    2. Create a new security group
    3. Add Ingress rule for TCP protocol to the security group
    4. Create an instance in the network/the security group
    5. Associate floating IP for the instance
    6. Connect to the instance via ssh and floating IP
    7. Without stopping ssh-connection disassociate floating ip from vm
    8. Check that connection is stopped
    9. Connect to the instance via ssh and floating IP again
    10. Check that connection is unreacheable


Expected results
################

All steps must be completed successfully, without any errors.
