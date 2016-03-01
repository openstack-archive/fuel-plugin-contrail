============
VMWare tests
============


Pre-condition
------------------------
   * Installed `Fuel 7.0
     <https://docs.mirantis.com/openstack/fuel/fuel-7.0/quickstart-guide.html#introduction>`_
   * Installed contrail plugin :doc:`/install_guide`
   * Environment must be created with "vCenter" support for compute virtualization and
     Contrail for networking
   * vSphere environments must be already preconfigured
   * ESXi hosts must have connectivity with Fuel Private network
   * A DHCP server capable of address reservation must be present in Private network
     to assign IP addresses to ContrailVMs


BVT Contrail VMWare test
------------------------


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
    3. Add nodes with following roles:
       * Controller
       * Compute
       * ComputeVMWare
       * Contrail-config + contrail-control + contrail-db
    4. Configure interfaces on nodes.
    5. Configure network settings.
    6. Configure Openstack settings:
       * Set VMWare vCenter/ESXi datastore for images (Glance)VMWare
         vCenter/ESXi datastore for images (Glance).
    7. Configure VMware vCenter Settings:
       Add and assign 2 vCenter clusters to compute-vmware.
    8. Configure Contrail plugin settings.
    9. Deploy the cluster.
    10. Run OSTF tests.


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
       * Storage: default
       * Additional services: default
    3. Configure Openstack settings:
       * Enable Ceph RBD for volumes (Cinder)
       * Enable Ceph RBD for images (Glance)
       * Enable Ceph RBD for ephemeral volumes (Nova)
       * Enable Ceph RadosGW for objects (Swift API)
    4. Add nodes with following roles:
       * Controller
       * Compute + Storage-Ceph OSD
       * Compute + Storage-Ceph OSD
       * Compute + Storage-Ceph OSD
       * ComputeVMWare
       * Contrail-config + contrail-control + contrail-db
    5. Configure interfaces on nodes.
    6. Configure network settings.
    7. Configure VMware vCenter Settings:
       Add and assign 1 vCenter clusters to compute-vmware.
    8. Configure Contrail plugin settings.
    9. Deploy the cluster.
    10. Run OSTF tests.


Expected results
################

Cluster should be deployed and all OSTF test cases should be passed.


Check redeployment Contrail and VMWare env after removing a controller node
---------------------------------------------------------------------------


ID
##

contrail_vmware_delete_controller


Description
###########

Check redeployment Contrail and VMWare env after removing a controller node


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
    3. Add nodes with following roles:
       * Controller
       * Controller
       * Controller
       * Controller
       * Compute + Cinder
       * ComputeVMWare
       * Contrail-config + contrail-control + contrail-db
    4. Configure interfaces on nodes.
    5. Configure network settings.
    6. Configure VMware vCenter Settings:
       Add and assign 2 vCenter clusters to compute-vmware.
    7. Configure Contrail plugin settings
    8. Deploy the cluster.
    9. Run OSTF tests.
    10. Delete primary controller node.
    11. Redeploy cluster.
    12. Run OSTF.


Expected results
################

Cluster should be deployed and all OSTF test cases should be passed.


Check conection between instances in different availibility zones.
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

    1. Connect to a Fuel with preinstalled Contrail plugin.
    2. Create a new environment with following parameters:
       * Compute: KVM/QEMU + vCenter
       * Networking: Neutron with tunneling segmentation
       * Storage: default
       * Additional services: default
    3. Add nodes with following roles:
       * Controller
       * Compute
       * ComputeVMWare
       * Contrail-config + contrail-control + contrail-db
    4. Configure interfaces on nodes.
    5. Configure network settings.
    6. Configure VMware vCenter Settings:
       Add and assign 2 vCenter clusters to compute-vmware.
    7. Configure Contrail plugin settings.
    8. Deploy the cluster.
    9. Run OSTF tests.
    10. Create net_1: net01__subnet, 192.168.1.0/24,
        and attach it to the default router.
    11. Launch instances with image TestVM
        and flavor m1.micro in nova availability zone.
    12. Launch instances with image TestVM-VMDK
        and flavor m1.micro in vcenter availability zone.
    13. Verify that instances on different hypervisors
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

    1. Connect to a Fuel with preinstalled Contrail plugin.
    2. Create a new environment with following parameters:
       * Compute: KVM/QEMU + vCenter
       * Networking: Neutron with tunneling segmentation
       * Storage: default
       * Additional services: default
    3. Add nodes with following roles:
       * Controller
       * ComputeVMWare
       * Compute
       * Contrail-config + contrail-control + contrail-db
    4. Configure interfaces on nodes.
    5. Configure network settings.
    6. Configure VMware vCenter Settings:
       Add and assign 2 vCenter clusters to compute-vmware.
    7. Configure Contrail plugin settings.
    8. Deploy the cluster.
    9. Run OSTF tests.
    10. Create net_1: net01__subnet, 192.168.1.0/24, and attach it to the router01.
    11. Create security groups:
        SG1
        SG2
    12. Delete all defaults egress rules of SG1 and SG2.
    13. Add icmp rule to SG1:
       Ingress rule with ip protocol 'icmp ', port range any, SG group 'SG1'
       Egress rule with ip protocol 'icmp ', port range any, SG group 'SG1'
    14. Add icmp rule to SG2:
       Ingress rule with ip protocol 'icmp ', port range any, SG group 'SG2'
       Egress rule with ip protocol 'icmp ', port range any, SG group 'SG2'
    15. Launch few instance of vcenter az with SG1 in net1(on each ESXI).
    16. Launch few instance of vcenter az with SG2 in net1(on each ESXI).
    17. Verify that icmp ping is enabled between VMs from SG1.
    18. Verify that icmp ping is enabled between instances from SG2.
    19. Verify that icmp ping is not enabled between instances from SG1 and VMs from SG2.


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

    1. Connect to a Fuel with preinstalled Contrail plugin.
    2. Create a new environment with following parameters:
       * Compute: KVM/QEMU + vCenter
       * Networking: Neutron with tunneling segmentation
       * Storage: default
       * Additional services: default
    3. Add nodes with following roles:
       * Controller
       * ComputeVMWare
       * Compute
       * Contrail-config + contrail-control + contrail-db
    4. Configure interfaces on nodes.
    5. Configure network settings.
    6. Configure VMware vCenter Settings:
       Add and assign 2 vCenter clusters to compute-vmware.
    7. Configure Contrail plugin settings.
    8. Deploy the cluster.
    9. Run OSTF tests.
    10. Launch few instances simultaneously with image TestVM-VMDK and flavor
        m1.micro in vcenter availability zone in  default internal network.
    11. Check connection between instances (ping, ssh).
    12. Delete all instances from horizon simultaneously.


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

    1. Connect to a Fuel with preinstalled Contrail plugin.
    2. Create a new environment with following parameters:
       * Compute: KVM/QEMU + vCenter
       * Networking: Neutron with tunneling segmentation
       * Storage: default
       * Additional services: default
    3. Add nodes with following roles:
       * Controller
       * CinderVMWare
       * ComputeVMWare
       * Compute
       * Contrail-config + contrail-control + contrail-db
    4. Configure interfaces on nodes.
    5. Configure network settings.
    6. Configure VMware vCenter Settings:
       Add and assign 2 vCenter clusters to compute-vmware.
    7. Configure Contrail plugin settings.
    8. Deploy the cluster.
    9. Run OSTF tests.
    10. Create instances.
    11. Create volumes.
    12. Attach each volume to its instance.


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
