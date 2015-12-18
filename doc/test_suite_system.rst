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


Check connectivity in different private networks on different nodes
-------------------------------------------------------------------


ID
##

contrail_vm_connection_in_diff_netw


Description
###########

Check connectivity between instances placed in different private networks and hosted on different nodes


Complexity
##########

Advanced


Steps
#####

    1. Login as admin to Openstack Horizon UI
    2. Create net01: net01__subnet and  net02: net02__subnet
    3. Launch vm1 in net01 network and vm2 in net02 network on different computes. Make sure that VMs were scheduled to different compute nodes. Otherwise, migrate vm2 to another compute
    4. Connect to the first instance via VNC (Horizon) and ping the second instance
    5. Connect to the second instance via VNC (Horizon) and ping the first instance
    6. Connect to Compute node via SSH and check the VM's connections with flow's command (flow -l)
    7. Ping not get response
    8. Login to Contrail WebUI
    9. Go to Configure, Policies, Create Network Policies
    10. Attach this policies to net01__subnet and  net02: net02__subnet
    11. Connect to the first instance via VNC (Horizon) and ping the second instance
    12. Connect to the second instance via VNC (Horizon) and ping the first instance
    13. Connect to Compute node via SSH and check the VM's connections with flow's command (flow -l)Ping should get a response
    14. Verify on Contrail controller WebUI that networks is there and VMs are attached to itPing should get a response, VMs are present  in Contrail controller WebUI


Expected results
################

Ping should get a response, VMs are present  in Contrail controller WebUI


Check connectivity in different private networks on a single node
-----------------------------------------------------------------


ID
##

contrail_vm_connection_on_single_node


Description
###########

Check connectivity between instances placed in different private networks and hosted on a single node


Complexity
##########

Advanced


Steps
#####

    1. Login as admin to Openstack Horizon UI
    2. Create net01: net01__subnet
    3. Launch 2 new instances: vm1 in net01 network and vm2 in default network. Make sure that VMs were placed on one compute nodes.
    4. Connect to the first instance via VNC (Horizon) and ping the second instance
    5. Connect to the second instance via VNC (Horizon) and ping the first instance
    6. Connect to Compute node via SSH and check the VM's connections with flow's command (flow -l)
    7. Verify on Contrail controller WebUI that network is there and VMs are attached to itAll steps must be completed successfully, without any errors.


Expected results
################

All steps must be completed successfully, without any errors.


Check connectivity for instances scheduled on a single compute in a single private network
------------------------------------------------------------------------------------------


ID
##

contrail_vm_connection_on_single_node_single_netw


Description
###########

Check connectivity for instances scheduled on a single compute in a single private network


Complexity
##########

Advanced


Steps
#####

    1. Login as admin to Openstack Horizon UI
    2. Create net01: net01__subnet
    3. Launch 2 new instances in net01 network. Make sure that VMs were placed on one compute nodes.
    4. Connect to the first instance via VNC (Horizon) and ping the second instance
    5. Connect to the second instance via VNC (Horizon) and ping the first instance
    6. Connect to Compute node via SSH and check the VM's connections with flow's command (flow -l)
    7. Verify on Contrail controller WebUI that network is there and VMs are attached to itAll steps must be completed successfully, without any errors.


Expected results
################

All steps must be completed successfully, without any errors.


Check ability to create stacks with contrail-specific atrributes from heat template
-----------------------------------------------------------------------------------


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
