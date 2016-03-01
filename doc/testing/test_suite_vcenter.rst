============
VMWare tests
============


Contrail VMWare Glance
----------------------


ID
##

contrail_vmvare_glance


Description
###########

Deploy a cluster with Contrail Plugin and VMWare data store as backend for glance.


Complexity
##########

smoke


Steps
#####

    1. Connect to a Fuel with preinstalled Contrail plugin.
    2. Create a new environment with following parameters:
       * Compute: KVM/QEMU + vCenter
       * Networking: Neutron with tunneling segmentation
       * Storage: default
       * Additional services: default
    3. Run script that prepares vmware part for deployment (creates few Distributed
       Switches and spawns virtual machine on each ESXi node)
    4. Configure Contrail plugin settings:
       * Datastore name
       * Datacenter name
       * Uplink for DVS external
       * Uplink for DVS private
       * DVS external
       * DVS internal
       * DVS private
    5. Add nodes with following roles:
       * Controller
       * Compute
       * ComputeVMWare
       * Contrail-config + contrail-control + contrail-db
    6. Configure interfaces on nodes.
    7. Configure network settings.
    8. Configure Openstack settings:
       * Set VMWare vCenter/ESXi datastore for images (Glance)VMWare
         vCenter/ESXi datastore for images (Glance).
    9. Configure VMware vCenter Settings:
       Add and assign 2 vCenter clusters to compute-vmware.
    10. Deploy the cluster.
    11. Run OSTF tests.


Expected results
################

Cluster should be deployed and all OSTF test cases should be passed.


Check deploy Contrail and VMWare with Ceph
------------------------------------------


ID
##

contrail_vmvare_ceph


Description
###########

Check deploy Contrail and VMWare with Ceph


Complexity
##########

smoke


Steps
#####

    1. Connect to a Fuel with preinstalled Contrail plugin.
    2. Create a new environment with following parameters:
       * Compute: KVM/QEMU + vCenter
       * Networking: Neutron with tunneling segmentation
       * Storage: Ceph
       * Additional services: default
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
       * Controller
       * Compute + Storage-Ceph OSD
       * Compute + Storage-Ceph OSD
       * Compute + Storage-Ceph OSD
       * ComputeVMWare
       * Contrail-config + contrail-control + contrail-db
       * Contrail-analytics + contrail-analytics-db
    6. Configure interfaces on nodes.
    7. Configure network settings.
    8. Configure VMware vCenter Settings:
       Add and assign 1 vCenter clusters to compute-vmware.
    9. Deploy the cluster.
    10. Run OSTF tests.


Expected results
################

Cluster should be deployed and all OSTF test cases should be passed.


Contrail VMWare delete controller
---------------------------------


ID
##

contrail_vmware_delete_controller


Description
###########

Verify that controller node can be deleted after deploy


Complexity
##########

smoke


Steps
#####

    1. Connect to a Fuel with preinstalled Contrail plugin.
    2. Create a new environment with following parameters:
       * Compute: KVM/QEMU + vCenter
       * Networking: Neutron with tunneling segmentation
       * Storage: default
       * Additional services: default
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
       * 3 Controller
       * Compute + Cinder
       * ComputeVMWare
       * Contrail-config + contrail-control + contrail-db + contrail-analytics
       * Contrail-analytics-db
    6. Configure interfaces on nodes.
    7. Configure network settings.
    8. Configure VMware vCenter Settings:
       Add and assign 2 vCenter clusters to compute-vmware.
    9. Deploy the cluster.
    10. Run OSTF tests.
    11. Delete primary controller node.
    12. Redeploy cluster.
    13. Run OSTF.


Expected results
################

Cluster should be deployed and all OSTF test cases should be passed.


Contrail VMWare add controller
---------------------------------


ID
##

contrail_vmware_add_controller


Description
###########

Verify that controller node can be added after deploy


Complexity
##########

smoke


Steps
#####

    1. Connect to a Fuel with preinstalled Contrail plugin.
    2. Create a new environment with following parameters:
       * Compute: KVM/QEMU + vCenter
       * Networking: Neutron with tunneling segmentation
       * Storage: Ceph(Glance)
       * Additional services: default
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
       * Controller + Storage-Ceph OSD
       * Compute + Cinder
       * ComputeVMWare
       * Contrail-config +  contrail-db
       * Contrail-analytics-db
       * contrail-control + contrail-analytics
    6. Configure interfaces on nodes.
    7. Configure network settings.
    8. Configure VMware vCenter Settings:
       Add and assign 2 vCenter clusters to compute-vmware.
    9. Deploy the cluster.
    10. Run OSTF tests.
    11. Add controller node.
    12. Redeploy cluster.
    13. Run OSTF.


Expected results
################

Cluster should be deployed and all OSTF test cases should be passed.


Check conection between instances in different availibility zones
-----------------------------------------------------------------


ID
##

contrail_vmvare_cross_az


Description
###########

Check connectivity between VMs in different availability zones.


Complexity
##########

smoke


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

contrail_vmvare_sg


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


Expected result
###############

Network traffic is allowed/prohibited to instances according security groups
rules.


Check creation instance of vcenter az in the one batch.
--------------------------------------------------------


ID
##

contrail_vmvare_one_batch


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


Expected result
###############

All instances should be created and deleted without any error.

Create volumes and attach them to appropriate instances.
----------------------------------------------------------------------------------------


ID
##

contrail_vmvare_volume


Description
###########

Create volumes and attach them to appropriate instances.


Complexity
##########

core


Steps
#####

    1. Login to Openstack Horizon UI
    2. Create instances.
    3. Create volumes.
    4. Attach each volume to its instance.


Expected result
###############

Each volume should be attached to its instance.

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
