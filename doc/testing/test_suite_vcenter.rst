============
VMWare tests
============


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
       * Compute: KVM/QEMU with vCenter
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
    6. Configure OpenStack settings:
       * Enable VMWare vCenter/ESXi datastore for images (Glance)
    7. Add 2 vSphere clusters and configure Nova Compute instances on conrollers and compute-vmware
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
       * Compute: KVM/QEMU with vCenter
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
    6. Add 2 vSphere clusters and configure Nova Compute instances on conrollers and compute-vmware
    7. Deploy the cluster.
    8. Run OSTF tests.


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
       * Additional services: default
    4. Add nodes with following roles:
       * Controller + MongoDB
       * Controller + MongoDB
       * Controller + MongoDB
       * Compute + CinderVMware
       * ComputeVMWare
       * ComputeVMWare
       * Contrail-config + contrail-control + contrail-db
    4. Configure interfaces on nodes.
    5. Configure network settings.
    6. Deploy the cluster.
    7. Add 2 vSphere clusters and configure Nova Compute instances on compute-vmware nodes
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
       * Compute: KVM/QEMU with vCenter
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
    4. Configure interfaces on nodes.
    5. Configure network settings.
    6. Add 2 vSphere clusters and configure Nova Compute instances on conrollers and compute-vmware
    7. Deploy the cluster.
    8. Run OSTF tests.
    9. Delete 1 node with controller role.
    10. Redeploy cluster.
    11. Run OSTF.


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
       * Compute: KVM/QEMU with vCenter
       * Networking: Neutron with tunneling segmentation
       * Storage: default
       * Additional services: default
    4. Add nodes with following roles:
       * Controller
       * Controller
       * Controller
       * ComputeVMWare
       * ComputeVMWare
       * Contrail-config + contrail-control + contrail-db
    4. Configure interfaces on nodes.
    5. Configure network settings.
    6. Add 2 vSphere clusters and configure Nova Compute instances on conrollers and compute-vmware
    7. Deploy the cluster.
    8. Run OSTF tests.
    9. Delete 1 node with ComputeVMWare role.
    10. Redeploy cluster.
    11. Run OSTF.
    12. Add 1 node with ComputeVMWare role.
    13. Redeploy cluster.
    14. Run OSTF.


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
       * Compute: KVM/QEMU with vCenter
       * Networking: Neutron with tunneling segmentation
       * Storage: default
       * Additional services: default
    4. Add nodes with following roles:
       * Controller
       * Controller
       * Controller
       * Contrail-config + contrail-control + contrail-db
    4. Configure interfaces on nodes.
    5. Configure network settings.
    6. Add 2 vSphere clusters and configure Nova Compute instances on conrollers and compute-vmware
    7. Deploy the cluster.
    8. Run OSTF tests.
    9. Add 1 node with CinderVMWare role.
    10. Redeploy cluster.
    11. Run OSTF.
    12. Delete 1 node with CinderVMWare role.
    13. Redeploy cluster.
    14. Run OSTF.


Expected results
################

Cluster should be deployed and all OSTF test cases should be passed.
