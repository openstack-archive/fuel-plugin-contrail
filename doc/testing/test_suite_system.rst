==============
System testing
==============


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
    2. Create 2 new tenants (the tenant networks under test must have intersecting or the same IP address spaces and the must be no policy enabled, which allows the traffic between tenants)
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
    2. Launch an instance using the default image, flavor and security group.
    3. Check that public IP 8.8.8.8 can be pinged from instance.
    4. Delete instance.


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
    4. Launch 2 new instance in the network with default security group
    5. Check ping connectivity between instances
    6. Verify on Contrail controller WebUI that network is there and VMs are attached to it


Expected results
################

The network is created, ping should get a response, VMs are present  in Contrail controller WebUI


Create and terminate networks and verify in Contrail UI
-------------------------------------------------------


ID
##

create_networks


Description
###########

Create and terminate networks and verify in Contrail UI


Complexity
##########

Advanced


Steps
#####

    1. Add 2 private networks via Horizon
    2. Verify that networks are present in Contrail UI
    3. Remove one of the private network via Horizon.
    4. Verify that the network is absent in Contrail UI
    5. Add a private network via Horizon.
    6. Verify that all networks are present in Contrail UI.


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

    1. Verify jumbo-frame and MTU configuration on all slaves
    2. Launch 2 new instances with default parameters
    3. Check ping connectivity between instances
    4. Connect to Compute Node via SSH and check the VM's connections with flow's command (flow -l)
    5. Verify on Contrail controller WebUI that network is there and VMs are attached to it


Expected results
################

All steps must be completed successfully, without any errors.


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


Check ability to a create contrail-specific attributes heat template
--------------------------------------------------------------------


ID
##

create_stacks_from_heat_template


Description
###########

Check ability to create stacks with contrail-specific attributes from heat template.


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


Check that ceilometer collects contrail metrics.
------------------------------------------------


ID
##

contrail_ceilometer_metrics


Description
###########

Check that ceilometer collects contrail metrics.


Complexity
##########

Core


Steps
#####

    1. Deploy Contrail cluster with ceilometer.
    2. Create 2 instances in the default network.
    3. Send icpm packets from one instance to another.
    4. Check contrail ceilometer metrics:
       "\*ip.floating.receive.bytes",
       "\*ip.floating.receive.packets",
       "\*ip.floating.transmit.bytes",
       "\*ip.floating.transmit.packets".


Expected results
################

All contrail ceilometer metrics should be collected by ceilometer.


Verify HTTPS on Contrail with selected TLS for OpenStack public endpoints
-------------------------------------------------------------------------


ID
##

https_tls_selected


Description
###########

Verify HTTPS on Contrail with selected TLS for OpenStack public endpoints


Complexity
##########

advanced


Steps
#####

    1. Deploy Contrail cluster with selected TLS for OPenStack public endpoints
    2. Get fingerprints from Openstack Horizon UI certificate
    3. Get fingerprints from Contrail UI certificate
    4. Get fingerprints from Contrail API certificate
    5. Verify that keys are identical


Expected results
################

All steps must be completed successfully, without any errors.


Verify that login and password can be changed
---------------------------------------------


ID
##

contrail_login_password


Description
###########

Verify that login and password can be changed


Complexity
##########

advanced


Steps
#####

    1. Deploy Contrail cluster
    2. Login as admin to Openstack Horizon UI
    3. Create new user
    4. Login as user to Openstack Horizon UI
    5. Change login and password for user
    6. Login to Openstack Horizon UI with new credentials
    7. Login to Contrail Ui with same credentials


Expected results
################

All steps must be completed successfully, without any errors.


Verify that RBAC works and can be changed
-----------------------------------------


ID
##

contrail_rbac


Description
###########

Verify that RBAC works and can be changed


Complexity
##########

advanced


Steps
#####

    1. Deploy Contrail cluster with RBAC enabled
    2. Create via ContrailUI API access for new member without delete permission
    3. Login as admin to Openstack Horizon UI
    4. Create new user with this access
    5. Verify via cli, that the permissions are applied
    6. Change in FuelUI AAA Mode to Admin cloud and apply it
    7. Verify via cli, that the RBAC permissions are not applied for the user


Expected results
################

All steps must be completed successfully, without any errors.


Check conection between instances in different availability zones
-----------------------------------------------------------------


ID
##

contrail_vmware_cross_az


Description
###########

Check connectivity between VMs in different availability zones.


Complexity
##########

advanced


Steps
#####

    1. Login to Openstack Horizon UI
    2. Create net_1: net01__subnet, 192.168.1.0/24,
       and attach it to the default router.
    3. Launch instances with image TestVM
       and flavor m1.micro in nova availability zone.
    4. Launch instances with image TestVM-VMDK
       and flavor m1.micro in vcenter availability zone.
    5. Check that instances are displayed in Contrail UI.
    6. Verify that instances on different hypervisors
       should communicate between each other.
       Send icmp ping from instances of vCenter to instances
       from Qemu/KVM and vice versa.


Expected results
################

VMs from different AZ should communicate via the same network. ICMP traffic is observed.


Security group rules with remote group id simple.
-------------------------------------------------


ID
##

contrail_vmware_sg


Description
###########

Verify that network traffic is allowed/prohibited to instances according security groups
rules.


Complexity
##########

core


Steps
#####

    1. Login to Openstack Horizon UI
    2. Create net_1: net01__subnet, 192.168.1.0/24, and attach it to the router01.
    3. Create security groups:
       SG1
       SG2
    4. Delete all defaults egress rules of SG1 and SG2.
    5. Add icmp rule to SG1:
       Ingress rule with ip protocol 'icmp ', port range any, SG group 'SG1'
       Egress rule with ip protocol 'icmp ', port range any, SG group 'SG1'
    6. Add icmp rule to SG2:
       Ingress rule with ip protocol 'icmp ', port range any, SG group 'SG2'
       Egress rule with ip protocol 'icmp ', port range any, SG group 'SG2'
    7. Launch few instance of vcenter az with SG1 in net1(on each ESXI).
    8. Launch few instance of vcenter az with SG2 in net1(on each ESXI).
    9. Verify that icmp ping is enabled between VMs from SG1.
    10. Verify that icmp ping is enabled between instances from SG2.
    11. Verify that icmp ping is not enabled between instances from SG1 and VMs from SG2.


Expected results
################

Network traffic is allowed/prohibited to instances according security groups
rules.


Check creation instance of vcenter az in the one batch.
-------------------------------------------------------


ID
##

contrail_vmware_one_batch


Description
###########

Create a batch of instances.


Complexity
##########

core


Steps
#####

    1. Login to Openstack Horizon UI
    2. Launch few instances simultaneously with image TestVM-VMDK and flavor
       m1.micro in vcenter availability zone in  default internal network.
    3. Check connection between instances (ping, ssh).
    4. Delete all instances from horizon simultaneously.


Expected results
################

All instances should be created and deleted without any error.


Check connectivity via external Contrail network with floating IP
-----------------------------------------------------------------


ID
##

contrail_vmware_ping_with/without_fip


Description
###########

Check connectivity VMs with external network with floating IP via Contrail network


Complexity
##########

Advanced


Steps
#####

    1. Login to Openstack Horizon UI
    2. Launch a new instance in the default network.
    3. Send ping from instance to 8.8.8.8 or any other IP outside the cloud
    4. Assign a Floating IP to the instance
    5. Send ping from instance to 8.8.8.8 or any other IP outside the cloud
    6. Allow incoming ICMP from any address in default security group.
    7. Send ping from external (HOST) machine to Floating IP (emulate external network)


Expected results
################

Instance should get ping responce from 8.8.8.8 or any other IP outside the cloud.
External (HOST) machine should get rping responce from instance.
