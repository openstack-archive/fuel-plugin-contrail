System testing
==============

Check connectivity between instances placed in a single private network and hosted on different nodes via Contrail network
--------------------------------------------------------------------------------------------------------------------------

**ID**

contrail_vm_connection_in_single_netw

**Description**
::

 Check connectivity between instances placed in a single private network and hosted on different nodes via Contrail network
 
**Complexity**

advanced

**Requre to automate**

Yes

**Steps**
::

 1. Login as admin to Openstack Horizon UI
 2. Create net01: net01__subnet
 3. Launch 2 new instances in net01 network. Make sure that VMs were scheduled to different compute nodes. Otherwise, migrate vm2 to another compute
 4. Connect to the first instance via VNC (Horizon) and ping the second instance
 5. Connect to the second instance via VNC (Horizon) and ping the first instance
 6. Connect to Compute Node via SSH and check the VM’s connections with flow’s command (flow -l)
 7. Verify on Contrail controller WebUI that network is there and VMs are attached to itPing should get a response, VMs are present  in Contrail controller WebUI

**Expected result**
 Ping should get a response, VMs are present  in Contrail controller WebUI

Check ip and gateway of VMs via Contrail network
------------------------------------------------

**ID**

check_ip_gateway_vm_via_contrail_network

**Description**
::

 Check ip and gateway of VMs via Contrail network

 
**Complexity**

advanced

**Requre to automate**

Yes

**Steps**
::

 1. Login as admin to Openstack Horizon UI
 2. Launch 1 new instance
 3. Verify correctness of instance's ip address according to the range, CIDR and gateway.
 4. Verify that this IP address was successfully received from DHCP (check the Horizon Logs tab for the instance)
 5. Connect to the instance via VNC (Horizon) and ping the gateway
 
**Expected Result**
 Ip address, mask and gateway are correct, ping should get a response 

Check no connectivity between VMs in different tenants via Contrail network
---------------------------------------------------------------------------

**ID**

contrail_vm_connection_in_different_tenants

**Description**
::

 Check no connectivity between VMs in different tenants via Contrail network
 
**Complexity**

advanced

**Requre to automate**

Yes

**Steps**
::

 1. Login as admin to Openstack Horizon UI
 2. Create 2 new tenants (the tenants under test must have intersecting or the same IP address spaces and the must be no policy enabled, which allows the traffic between tenants)
 3. Launch 2 new instance in different tenants
 4. Connect to the first instance via VNC (Horizon) and ping the second instance
 5. Connect to the second instance via VNC (Horizon) and ping the first instance
 6. Connect to Compute Node via SSH and check the VM’s connections
 7. Verify on Contrail controller WebUI that networks are there and VMs are attached to different networks.

**Expected Result**
 Ping should not get a response, VM’s connections should be in the different ethernet device, VMs are present  in Contrail controller WebUI

Check connectivity VMs with external network without floating IP via Contrail network
-------------------------------------------------------------------------------------

**ID**

contrail_vm_connection_withaut_floating_ip

**Description**
::

 Check connectivity VMs with external network without floating IP via Contrail network
 
**Complexity**

advanced

**Requre to automate**

Yes

**Steps**
::

 1. Login as admin to Openstack Horizon UI
 2. Launch a new instance
 3. Connect to the  instance via VNC (Horizon), send ping to 8.8.8.8 or any other IP outside the cloud and  ping an IP address of lab host which is a gateway for vSRX
 4. Verify on Contrail controller WebUI that network is there and VMs are attached to it
 5. Ping should get a response, VMs are present  in Contrail controller WebUI

**Expected Result**
 Ping should get a response, VMs are present  in Contrail controller WebUI

Create a new network via Contrail WebUI
---------------------------------------

**ID**

create_new_network_via_contrail

**Description**
::

 Create a new network via Contrail WebUI
 
 **Complexity**

advanced

**Requre to automate**

Yes

**Steps**
::

 1. Login as admin to Contrail WebUI
 2. Create a new network, a subnetwork
 3. Login as admin to Openstack Horizon UI
 4. Launch 2 new instance in the network
 5. Connect to the first instance via VNC (Horizon) and ping the second instance
 6. Verify on Contrail controller WebUI that network is there and VMs are attached to itThe network is created, Ping should get a response, VMs are present  in Contrail controller WebUI

**Expected Result**
 The network is created, Ping should get a response, VMs are present  in Contrail controller WebUI
 
Check connectivity VMs with external network with floating IP via Contrail network
----------------------------------------------------------------------------------

**ID**

contrail_vm_connection_with_floating_ip

**Description**
::

 Check connectivity VMs with external network with floating IP via Contrail network
 
**Complexity**

advanced

**Requre to automate**

Yes

**Steps**
::

 1. Login as admin to Openstack Horizon UI
 2. Launch a new instance
 3. Login on Contrail controller WebUI and verify that VMs are attached to it
 4. Assign a Floating IP to the VM via Contrail controller WebUI
 5. Connect to the  instance via VNC (Horizon) and send ping to 8.8.8.8 or any other IP outside the cloud
 6. Allow ping in Security group section via Contrail WebUI
 7. Send ping from external  (HOST) machine to Floating IP (emulate external network)Floating IP is added, Ping should get a response, VMs are present  in Contrail controller WebUI

**Expected result**
 Floating IP is added, Ping should get a response, VMs are present  in Contrail controller WebUI

Testing aggregation of network interfaces (bonding)
---------------------------------------------------

**ID**

check_bonding_with_contrail

**Description**
::

 Verify bonding with Contrail Plugin
 
**Complexity**

advanced

**Requre to automate**

Yes

**Steps**
::

 1. Login in Fuel web UI
 2. Press “New OpenStack Environment”
 3. Set Environment Name = ‘test’ 
 4. Set QEMU or KVM as compute
 5. Select 'Neutron with tunneling segmentation' as a network configuration
 6. Set “default” glance and cinder
 7. Do not use any Additional Services
 8. Press “Create”
 9. Press “Settings” tab
 10. Enable “Contrail” Plugin and configure it
 11. Add 3 nodes with “contrail-db”, "contarail-config" and "contrail-control" roles on all nodes
 12. Add 1 node with “Controller” role
 13. Add 1 node with “Compute” role
 14. Bond Storage and Management ethernet interfaces with “Active Backup” mode and to establish a private network here
 15. Start deploy
 16. Check Controller and Contrail nodes status
 17. After the end of deploy run OSTF tests
 18. Add 1 node with “Controller” role
 19. Add 1 node with “Compute” role
 20. Start deploy
 21. After the end of deploy run OSTF tests

**Expected result**
 All steps must be completed successfully, without any errors.

Uninstall of plugin
-------------------

**ID**

uninstall_contrail_plugin

**Description**
::

 Uninstall of plugin
 
**Complexity**

advanced

**Requre to automate**

Yes

**Steps**
::

 1. Remove plugin: fuel plugins --remove <fuel-plugin-name>==<fuel-plugin-version>
 2. Check that it was removed successfully: fuel pluginsContrail plugin was removed successfully.

**Expected Result**
 Contrail plugin was removed successfully.

Uninstall of plugin with deployed environment
---------------------------------------------

**ID**

uninstall_contrail_plugin_with_deployed_environment

**Description**
::

 Uninstall of plugin with deployed environment
 
**Complexity**

advanced

**Requre to automate**

Yes

**Steps**
::

 1. Try to remove plugin and ensure that alert presents in cli: “400 Client Error: Bad Request (Can not delete plugin which is enabled for some environment.)” 
 2. Remove environment
 3. Remove plugin
 4. Check that it was removed successfully

**Expected result**
 Alert is present when we try to remove plugin which is attached to enabled environment. When environment was removed, plugin is removed successfully too.
 

Create and terminate networks and verify it in Contrail UI
----------------------------------------------------------

**ID**

create_networks

**Description**
::

 Create and terminate networks and verify it in Contrail UI
 
**Complexity**

advanced

**Requre to automate**

Yes

**Steps**
::

 1. Add private networks net_01 and net_02.Verify that networks are present in Contrail UI
 2. Remove private network net_01.Verify that network net_01 absent in Contrail UI
 3. Add private network net_01.Verify that net_01 and net_02 are present in Contrail UI

**Expected Result**
 All steps must be completed successfully, without any errors.
 

Deploy cluster with 2 node groups
---------------------------------

**ID**

deploy_neutron_gre_nodegroups

**Description**
::

 Deploy cluster with 2 node groups

**Complexity**

advanced

**Requre to automate**

Yes

**Steps**
::

 1. Configure 2 networks sets for slaves
 2. Create cluster with Neutron GRE
 3. Add 3 controller nodes from default nodegroup
 4. Add 3 compute nodes from custom nodegroup
 5. Add 3 contrail controller nodes from default nodegroup
 6. Deploy cluster
 7. After the end of deploy run OSTF tests

**Expected result**
 All steps must be completed successfully, without any errors.

Verify traffic flow in jumbo-frames-enabled network
---------------------------------------------------

**ID**

traffic_flow_in_jumbo-frames-enabled_network

**Description**
::

 Verify traffic flow in jumbo-frames-enabled network
 
**Complexity**

advanced

**Requre to automate**

Yes

**Steps**
::

 1. Login as admin to Openstack Horizon UI
 2. Launch 2 new instances with default parameters
 3. Connect to the first instance via VNC (Horizon) and ping the second instance
 4. Connect to the second instance via VNC (Horizon) and ping the first instance
 5. Connect to Compute Node via SSH and check the VM’s connections with flow’s command (flow -l)
 6. Verify on Contrail controller WebUI that network is there and VMs are attached to it

**Expected result**
 All steps must be completed successfully, without any errors.

Verify connectivity between vms with the same internal ips in different tenants
-------------------------------------------------------------------------------

**ID**

connectivity_vms_with_the_same_internal_ips_in_different_tenants

**Description**
::

 Verify connectivity between vms with the same internal ips in different tenants

**Complexity**

advanced

**Requre to automate**

Yes

**Steps**
::

 1. Login as admin to Openstack Horizon UI
 2. Create 2 new tenants
 3. Navigate to Identity -> Projects.
 4. Click on Create Project.
 5. Type name ‘test_1’ of tenant.
 6. Click on Create Project.
 7. Type name ‘test_2’ of tenant.
 8. On tab Project Members add admin with admin and member.
 9. In tenant ‘test_1’  create net1 and subnet1 with CIDR 10.0.0.0/24
 10. In tenant ‘test_1’  create security group ‘SG_1’ and add rule that allows ingress icmp traffic
 11. In tenant ‘test_2’  create net2 and subnet2 with CIDR 10.0.0.0/24
 12. In tenant ‘test_2’ create security group ‘SG_2’ and add rule that allows ingress icmp traffic
 13. In tenant ‘test_1’ boot 2 VMs in net1 specifying ‘SG_1’ as security group: test1 with ip 10.0.0.4 and test2 with ip 10.0.0.5
 14. In tenant ‘test_2’ boot 2 VMs: test3 with ip 10.0.0.4 and test4 with ip 10.0.0.5
 15. Go to test1 and ping test2 – pings should pass
 16. Verify that VMs with same ip on different tenants should communicate between each other. Send icmp ping from VM _1 to VM_3,  VM_2 to Vm_4 and vice versa

**Expected Result**
 All steps must be completed successfully, without any errors.

Launch instance with new security group and check connection after deleting icmp and tcp rules
----------------------------------------------------------------------------------------------

**ID**

launch_instances_with_new_security_group

**Description**
::

 Launch instance with new security group and check connection after deleting ICMP and TCP rules

**Complexity**

advanced

**Requre to automate**

Yes

**Steps**
::

 1. Login as admin to Openstack Horizon UI
 2. Launch instance VM_1 in the network net_02 with image TestVMDK and flavor m1.micro in the nova az.
 3. Launch instance VM_2  in the network net_02  with image TestVMDK and flavor m1.micro.
 4. Verify that instances are present in Contrail UI
 5. Create security group SG_1 to allow ICMP traffic.
 6. Add Ingress rule for ICMP protocol to SG_1
 7. Add Egress rule for ICMP protocol to SG_1
 8. Attach SG_1 to VMs
 9. Check ping between VM_1 and VM_2 and vice verse
 10. Create security group SG_2 to allow TCP traffic port 22.
 11. Add Ingress rule for TCP protocol port 22 to SG_2
 12. Add Egress rule for TCP protocol port 22 to SG_2
 13. Attach SG_2 to VMs
 14. ssh from VM_1 to VM_2 and vice verseVMs should be pingable and accessible via ssh from each other
 15. Delete all rules from SG_1 and SG_2
 16. Check no ping and no ssh from VM_1 to VM_2  and vice verse
 17. Add Ingress rule for ICMP protocol to SG_1
 18. Add Egress rule for ICMP protocol to SG_1
 19. Add Ingress rule for TCP protocol port 22 to SG_2
 20. Add Egress rule for TCP protocol port 22 to SG_2
 21. Check ping between VM_1 and VM_2 and vice verse
 22. Check SSh from VM_1 to VM_2 and vice verse
 23. Delete security groups.
 24. Attach VMs to default security group.
 25. Check ping between VM_1 and VM_2 and vice verse
 26. Check ssh from VM_1 to VM_2 and vice verse
 27.Ping should get a response 

**Expected Result**
 Ping should get a response 

Check connectivity between instances placed in different private networks and hosted on different nodes
-------------------------------------------------------------------------------------------------------

**ID**

contrail_vm_connection_in_diff_netw

**Description**
::

 Check connectivity between instances placed in different private networks and hosted on different nodes 
 
**Complexity**

advanced

**Requre to automate**

Yes

**Steps**
::

 1. Login as admin to Openstack Horizon UI
 2. Create net01: net01__subnet and  net02: net02__subnet
 3. Launch vm1 in net01 network and vm2 in net02 network on different computes. Make sure that VMs were scheduled to different compute nodes. Otherwise, migrate vm2 to another compute
 4. Connect to the first instance via VNC (Horizon) and ping the second instance
 5. Connect to the second instance via VNC (Horizon) and ping the first instance
 6. Connect to Compute node via SSH and check the VM’s connections with flow’s command (flow -l)
 7. Ping not get response
 8. Login to Contrail WebUI 
 9. Go to Configure, Policies, Create Network Policies
 10. Attach this policies to net01__subnet and  net02: net02__subnet
 11. Connect to the first instance via VNC (Horizon) and ping the second instance
 12. Connect to the second instance via VNC (Horizon) and ping the first instance
 13. Connect to Compute node via SSH and check the VM’s connections with flow’s command (flow -l)Ping should get a response
 14. Verify on Contrail controller WebUI that networks is there and VMs are attached to itPing should get a response, VMs are present  in Contrail controller WebUI


**Expected Result**
 Ping should get a response, VMs are present  in Contrail controller WebUI

Check connectivity between instances placed in different private networks and hosted on a single node
-----------------------------------------------------------------------------------------------------

**ID**

contrail_vm_connection_on_single_node

**Description**
::

  Check connectivity between instances placed in different private networks and hosted on a single node 
  
**Complexity**

advanced

**Requre to automate**

Yes

**Steps**
::

 1. Login as admin to Openstack Horizon UI
 2. Create net01: net01__subnet
 3. Launch 2 new instances: vm1 in net01 network and vm2 in default network. Make sure that VMs were placed on one compute nodes. 
 4. Connect to the first instance via VNC (Horizon) and ping the second instance
 5. Connect to the second instance via VNC (Horizon) and ping the first instance
 6. Connect to Compute node via SSH and check the VM’s connections with flow’s command (flow -l)
 7. Verify on Contrail controller WebUI that network is there and VMs are attached to itAll steps must be completed successfully, without any errors.

**Expected Result**
 All steps must be completed successfully, without any errors.

Check connectivity for instances scheduled on a single compute in a single private network
------------------------------------------------------------------------------------------

**ID**

contrail_vm_connection_on_single_node_single_netw

**Description**
::

 Check connectivity for instances scheduled on a single compute in a single private network
 
**Complexity**

advanced

**Requre to automate**

Yes

**Steps**
::

 1. Login as admin to Openstack Horizon UI
 2. Create net01: net01__subnet
 3. Launch 2 new instances in net01 network. Make sure that VMs were placed on one compute nodes.
 4. Connect to the first instance via VNC (Horizon) and ping the second instance
 5. Connect to the second instance via VNC (Horizon) and ping the first instance
 6. Connect to Compute node via SSH and check the VM’s connections with flow’s command (flow -l)
 7. Verify on Contrail controller WebUI that network is there and VMs are attached to itAll steps must be completed successfully, without any errors.

**Expected Result**
 All steps must be completed successfully, without any errors.
 

Check ability to create stacks with contrail-specific atrributes from heat template.
---------------------------------------------------------------------

**ID**

create_stacks_from_heat_template

**Description**
::

 Check ability to create stacks with contrail-specific atrributes from heat template.
 
**Complexity**

advanced

**Requre to automate**

No

**Steps**
::

 1. Create stack with heat template.
 2. Check that stack was created.
 
**Expected Result**
 Stack should be created.