============
VMWare tests
============


Pre-condition
------------------------
   * Installed `Fuel 8.0
     <https://docs.mirantis.com/openstack/fuel/fuel-8.0/quickstart-guide.html#introduction>`_
   * Installed contrail plugin :doc:`/install_guide`
   * Environment must be created with "vCenter" support for compute
   * vSphere environments must be already preconfigured
   * vCenter server and ESXi hosts must have connection to private network
   * User must provide dhcp server with reservation ip addresses for
     ContrailVMs. That's mean that you need to bind ip-addresses to
     mac-addresses for each ContrailVMs.


BVT Contrail VMWare test
------------------------


ID
##

contrail_vmvare_bvt_glance


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
       * Controller
       * Controller
       * Compute + Cinder
       * CinderVMWare
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
    8. Deploy the cluster.
    9. Run OSTF tests.


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
       * ComputeVMWare
       * Contrail-config + contrail-control + contrail-db
    4. Configure interfaces on nodes.
    5. Configure network settings.
    6. Configure VMware vCenter Settings:
       Add and assign 1 vCenter clusters to compute-vmware.
    7. Configure Contrail plugin settings.
    8. Deploy the cluster.
    9. Run OSTF tests.


Expected results
################

Cluster should be deployed and all OSTF test cases should be passed.


Check deploy Contrail and VMWare with Ceilometer
------------------------------------------------


ID
##

contrail_vmvare_ceilometer


Description
###########

Check deploy Contrail and VMWare with Ceilometer


Complexity
##########

smoke


Steps
#####

    1. Connect to a Fuel with preinstalled Contrail plugin.
    2. Create a new environment with following parameters:
       * Compute: KVM/QEMU with vCenter
       * Networking: Neutron with tunneling segmentation
       * Storage: default
       * Additional services: Ceilometer
    4. Add nodes with following roles:
       * Controller + MongoDB
       * Controller + MongoDB
       * Controller + MongoDB
       * Compute + CinderVMware
       * ComputeVMWare
       * Contrail-config + contrail-control + contrail-db
    4. Configure interfaces on nodes.
    5. Configure network settings.
    6. Configure VMware vCenter Settings:
       Add and assign 2 vCenter clusters to compute-vmware.
    7. Configure Contrail plugin settings.
    8. Deploy the cluster.
    8. Run OSTF tests.


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
    4. Add nodes with following roles:
       * Controller
       * Controller
       * Controller
       * Controller
       * Compute + Cinder
       * ComputeVMWare
       * CinderVMWare
       * Contrail-config + contrail-control + contrail-db
    5. Configure interfaces on nodes.
    6. Configure network settings.
    7. Configure VMware vCenter Settings:
       Add and assign 2 vCenter clusters to compute-vmware.
    8. Configure Contrail plugin settings
    9. Deploy the cluster.
    10. Run OSTF tests.
    11. Delete 1 node with controller role.
    12. Redeploy cluster.
    13. Run OSTF.


Expected results
################

Cluster should be deployed and all OSTF test cases should be passed.


Check redeployment Contrail and VMWare env after remove, add a computeVMWare
----------------------------------------------------------------------------


ID
##

contrail_delete_add_computeVMware


Description
###########

Check redeployment Contrail and VMWare env after remove, add a computeVMWare


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
    4. Add nodes with following roles:
       * Controller
       * Controller
       * Controller
       * ComputeVMWare
       * Contrail-config + contrail-control + contrail-db
    4. Configure interfaces on nodes.
    5. Configure network settings.
    6. Configure VMware vCenter Settings:
       Add and assign 2 vCenter clusters to compute-vmware.
    7. Configure Contrail plugin settings
    8. Deploy the cluster.
    9. Run OSTF tests.
    10. Delete 1 node with ComputeVMWare role.
    11. Redeploy cluster.
    12. Run OSTF.
    13. Add 1 node with ComputeVMWare role.
    14. Redeploy cluster.
    15. Run OSTF.


Expected results
################

Cluster should be deployed and all OSTF test cases should be passed.


Check redeployment Contrail and VMWare env after remove, add a cinderVMware
---------------------------------------------------------------------------


ID
##

contrail_delete_add_cinderVMware


Description
###########

Check redeployment Contrail and VMWare env after remove, add a cinderVMware


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
    4. Add nodes with following roles:
       * Controller
       * Controller
       * Controller
       * ComputeVMWare
       * Contrail-config + contrail-control + contrail-db
    4. Configure interfaces on nodes.
    5. Configure network settings.
    6. Configure VMware vCenter Settings:
       Add and assign 2 vCenter clusters to compute-vmware.
    7. Configure Contrail plugin settings
    8. Deploy the cluster.
    9. Run OSTF tests.
    9. Add 1 node with CinderVMWare role.
    11. Redeploy cluster.
    12. Run OSTF.
    13. Delete 1 node with CinderVMWare role.
    14. Redeploy cluster.
    15. Run OSTF.


Expected results
################

Cluster should be deployed and all OSTF test cases should be passed.
