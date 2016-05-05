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

   - Installed `Fuel 9.0 <https://docs.mirantis.com/openstack/fuel/fuel-9.0/quickstart-guide.html#introduction>`_
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

Configuration
-------------
To install environment with Contrail and VMWware support you should proceed with following steps:

#. install pyvmomi

#. Assign all planned roles (including **single compute-vmware** role) in Nodes tab from Fuel UI

   .. image:: images/fuel_assign_roles.png

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

#. Check that provisioning scripts were run on primary-controller by checking their marker files:

    ::

      root@node-34:~# ls /opt/contrail/*-DONE
      /opt/contrail/change_hostname-10.109.3.249-DONE         /opt/contrail/provision_contrailvm-10.109.3.249-DONE
      /opt/contrail/disable_add_vnc_config-10.109.3.249-DONE  /opt/contrail/reboot_contrailvm-10.109.3.249-DONE
      /opt/contrail/fab_prepare_contrailvm-DONE               /opt/contrail/register_contrailvm_vrouter-10.109.3.249-DONE
      /opt/contrail/fab_setup_vcenter-DONE                    /opt/contrail/set_ntp-10.109.3.249-DONE

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
  - *vSphere cluster* - comma separated list of vSphere clusters
  - *Service name* - nova-compute service name on compute-vmware
  - *Datastore regex* - Datastore regex
  - *Target node* - Target node for nova-compute service

**From Fuel Contrail plugin settings:**

  - *Environment type* - this setting defines the flavor for ContrailVM.
    If set to "development" ContrailVM will spawn with 2GB RAM otherwise it will use 8GB.
  - *vCenter Datacenter* - name of vCenter Datacenter
  - *vCenter dvSwitch* - name of vCenter dvSwitch
  - *vCenter DV Port Group* - name of Port Group in vCenter dvSwitch
  - *vCenter DV Port Group number of ports* - number of ports in vCenter Port Group
  - *ntp server for ContrailVM* - ntp server available for ContrailVM
  - *vCenter ESXi data for fabric* - vCenter ESXi data for fabric in YAML format

  **vCenter ESXi data for fabric**
  - data in YAML format which describes the ESXi hosts. As Fuel is not managing ContrailVMs directly
    as slave nodes, all operations on ContrailVMs are done by fabric scripts run on OpenStack primary
    controller. They use testbed.py as configuration file, which is populated by plugin tasks which
    use data from plugin settings.

  *Example:*
|    esxi1:
|      username: "root"
|      password: "swordfish"
|      ip: "172.16.0.250"
|      fabric_vswitch: "vSwitch1"
|      uplink_nic: "vmnic1"
|      contrail_vm:
|        mac: "00:50:56:03:BC:BA"
|        host: "root@10.109.3.249"
|      cluster: "Cluster2"
|      datastore: "/vmfs/volumes/nfs"
|    esxi2:
|      username: "root"
|      password: "swordfish"
|      ip: "172.16.0.253"
|      fabric_vswitch: "vSwitch1"
|      uplink_nic: "vmnic1"
|      contrail_vm:
|        mac: "00:50:56:03:BC:BB"
|        host: "root@10.109.3.247"
|      cluster: "Cluster1"
|      datastore: "/vmfs/volumes/nfs"

*parameter description*
  - *username* - username of esxi user
  - *password* - password of esxi user
  - *ip* - IP address of ESXi server
  - *fabric_vswitch* - virtual switch name for IP fabric. This switch will provide connectivity to
    Fuel Private network for ContrailVMs
  - *uplink_nic* - NIC name attached to fabric_switch virtual switch. This interface must have connectivity
    with Fuel Private network.
  - *contrail_vm:mac* - MAC address for ContrailVM first interface (eth0) connected to IP fabric.
  - *contrail_vm:host* - user and ip addrress for ContrailVM. These credentials will be used for ContrailVM
    provisioning, please make sure that proper DHCP reservation was created.
  - *cluster* - name of vCenter cluster
  - *datastore* - path to datastore
