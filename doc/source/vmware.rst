Contrail with VMware vCenter
============================

Overview
--------

Starting from Contrail Release 3.0.0, it is possible to integrate Contrail with the VMware vCenter
acting as an Openstack compute node.

This topic describes how configure Fuel Contrail Plugin to work with existing or already provisioned
vSphere deployments that use OpenStack as the main orchestrator.

Integration with vCenter include two main roles: compute-vmware and contrail-vmware. As the basis for compute-vmware role will use default Fuel compute-vmware role. Compute-vmware will be located on the openstack side of hybrid environment and will include nova-compute with Contrail Nova vCenter driver. One compute-vmware will serve one vCenter. In the current release work with multiple vCenter instances is not supported. Compute-vmware role will be not compatible with any other role. Contrail-vmware will be located on vmware side of hybrid environment and will include Contrail vRouter. One contrail-vmware must to be installed on each ESXi node. Contrail-vmware role will not be compatible with any other role. Integration assumes that vmware part of the environment already exists - datacenter and clusters are created. Deployment of the environment will include 2 stages. During the 1st stage user will run script that prepares vmware part for deployment (creates few Distributed Switches and spawns virtual machine on each ESXi node). The rest of management will provided by the Fuel master

    .. image:: images/contrail_vmware_openstack.png

Prerequisites
-------------

   - Installed `Fuel 9.1 <https://docs.mirantis.com/openstack/fuel/fuel-9.0/quickstart-guide.html#introduction>`_
   - Installed Fuel Contrail Plugin :doc:`/install_guide`
   - Environment must be created with "vCenter" support for compute virtualization and Contrail for networking
   - vSphere environments must be already preconfigured
   - pyvmomi python package need to be installed for vmware provision script


Restrictions
------------

  - There must be a single vmware-compute node for each vCenter
  - Compute-vmware role can not be combined with any other roles
  - Contrail-vmware role can not be combined with any other roles
  - The environment must contain at least one KVM/QEMU compute node
  - According contrail package (version: 3.1.0.0-25) `bug <https://docs.mirantis.com/openstack/fuel/fuel-9.0/quickstart-guide.html#introduction>`_ we can use only one cluster per Datacenter.
  - All ESXi hosts in vCenter cluster must have instance with contrail-vmware role

Configuration
-------------
To install environment with Contrail and VMWware support you should proceed with following steps:

#. Install pyvmomi module

    ::

      [root@nailgun ~]# easy_install pyvmomi

#. Fill vmware credentials in Fuel vmware tab

   .. image:: images/fill_vmware_credentials.png

#. Run script that will spawn ContrailVM's, DVS's

    ::

      [root@nailgun ~]# cd /var/www/nailgun/plugins/contrail-5.1/deployment_scripts/
      [root@nailgun deployment_scripts]# ./spawner.py --env_id 1 --spawn

#. Wait a few minutes when ContrailVM's node will be arrived

   .. image:: images/contrailvms_arrived.png

#. To verified if the nodes from vmware you may check "Node Information"

   .. image:: images/contrailvms_verified.png

#. Assign all planned roles (including **single compute-vmware** role and contrail-vmware for each ESXi host) in Nodes tab from Fuel UI

   .. image:: images/fuel_assign_roles.png

#. ContrailVM's will be spawned with 3 network interfaces (the first two for fuel networks and third for vmware connection) therefore we assume that public, storage and management network will use vlan tagging

   .. image:: images/contrailvm_vlan_tagging.png

#. Fill settings in VMware tab from Fuel UI

   .. image:: images/vmware_tab_settings.png

#. Fill additional settings in Fuel Contrail plugin settings from Fuel UI

   .. image:: images/additional_vmware_settings.png

#. Deploy environment

Verification
------------
After deploy finishes, you can verify your installation.

#. Check that Contrail services are running on compute node:

    ::

      root@node-35:~# contrail-status
      == Contrail vRouter ==
      supervisor-vrouter:           active
      contrail-vrouter-agent        active
      contrail-vrouter-nodemgr      active

#. Check that Contrail services are running on ContrailVM:

    ::

      root@ContrailVM-249:~# contrail-status
      == Contrail vRouter ==
      supervisor-vrouter:           active
      contrail-vrouter-agent        active
      contrail-vrouter-nodemgr      active



VMware related options
----------------------
**From VMware tab:**
  - *Availability zone* - openstack availability zone name
  - *vCenter host* - vCenter host or IP
  - *vCenter username* - vCenter username
  - *vCenter password* - vCenter password
  - *vSphere cluster* - name of vSphere cluster
  - *Service name* - nova-compute service name on compute-vmware
  - *Datastore regex* - Datastore regex
  - *Target node* - Target node for nova-compute service

**From Fuel Contrail plugin settings:**

  - *ESXi datastore name* - Name of datastore where ContrailVM will be spawned
  - *ESXi uplink admin* - Name of interface that provide connection between ESXi node and Fuel admin network
  - *ESXi uplink private* - Name of interface that provide connection between ESXi node and Fuel private network
  - *vCenter Datacenter name* - name of vCenter Datacenter
  - *External DVS name* - Name of DVS that provide connection between ESXi and Fuel admin network
  - *Private DVS name* - Name of DVS that provide connection between ESXi and Fuel private network
  - *Internal DVS name* - Name of DVS need for internal contrail traffic

*spawer.py parameter description:*
  - *--env_id*(type int) - id of Fuel environment (mandatory parameter)
  - *--spawn*(type boolean) - spawn vm's for contrail-vmware role. When run script with this parameter it will take credential from Fuel vmware tab, create dvs's with port groups, spawn vm's on each ESXi host in cluster and attach their to all dvs's.
  - *--map-ips*(type boolean) - this need for internal plugin calculations
  - *--dvs-mtu-ext*(type int) - set max MTU for external DVS
  - *--dvs-mtu-priv*(type int) - set max MTU for private DVS
  - *--dvs-mtu-int*(type int) - set max MTU for internal DVS
  - *--cluster-list*(type str) - change cluster list in Fuel. This option is deprecated no need to you it.
  - *--reduce-vm-params*(type boolean) - Reduce memory value for ContrailVM's, for production purposes this parameter not recommend to use.

Add and delete ESXi hosts
-------------------------

**Add ESXi host:**

#. Add ESXi host to vCenter cluster manually

#. Run script that will spawn additional ContrailVM

    ::

      [root@nailgun ~]# cd /var/www/nailgun/plugins/contrail-5.1/deployment_scripts/
      [root@nailgun deployment_scripts]# ./spawner.py --env_id 1 --spawn

#. Wait a few minutes when ContrailVM's node will be arrived
#. Assign contrail-vmware role on new ContrailVM
#. Run "Deploy Changes"

**Remove ESXi host:**

#. In Fuel UI remove contrail-vmware instance that located on ESXi host which you want to remove.
#. Run "Deploy Changes"
#. Remove ESXi host from vCenter cluster manually
