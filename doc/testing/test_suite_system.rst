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

    1. Install contrail plugin.
    2. Create an environment with "Neutron with tunneling
       segmentation" as a network configuration.
    3. Enable and configure Contrail plugin.
    4. Add a node with "controller" + "MongoDB" multirole.
    5. Add a node with "compute".
    6. Add a node with "contrail-config", "contrail-control" and
       "contrail-db" roles.
    7. Deploy cluster with plugin.
    8. Run OSTF tests.
    9. Create 2 instances in the default network.
    10. Send icpm packets from one instance to another.
    11. Check contrail ceilometer metrics:
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
