Contrail with VMware vCenter
============================

Overview
--------

Starting from Contrail Release 3.0.0, it is possible to integrate Contrail with the VMware vCenter
acting as an Openstack compute node.

This topic describes how configure Fuel Contrail Plugin to work with existing or already provisioned
vSphere deployments that use openstack as the main orchestrator.

The Contrail VMware vCenter solution is comprised of the following two main components:

Control and management that runs the following components as needed per Contrail system:
A VMware vCenter Server independent installation, that is not managed by Juniper Contrail.
The automation scripts provision vCenter with Contrail components and create entities required to run Contrail.
The Contrail controller, including the configuration nodes, control nodes, analytics, database, and
Web UI, which is installed, provisioned, and managed by Fuel Contrail Plugin.
A VMware vCenter plugin provided with Contrail that resides on the compute-vmware node.
VMware ESXi virtualization platforms forming the compute cluster, with Contrail data plane (vRouter)
components running inside an Ubuntu-based virtual machine. The virtual machine, named ContrailVM,
forms the compute personality while performing Contrail installs. The ContralVM is set up and provisioned
by automation scripts. There is one ContrailVM running on each ESXi host.
The following figure shows various components of the solution.

    .. image:: images/contrail_vmware_openstack.png

Prerequisites
-------------

   - Installed `Fuel 8.0 <https://docs.mirantis.com/openstack/fuel/fuel-8.0/quickstart-guide.html#introduction>`_
   - Installed Fuel Contrail Plugin :doc:`/install_guide`
   - Environment must be created with "vCenter" support for compute virtualization and Contrail for networking
   - vSphere environments must be already preconfigured
   - ESXi hosts must have connectivity with Fuel Private network
   - A DHCP server capable of address reservation must be present in Private network to assign IP addresses to ContrailVMs

Restrictions
------------

  - There must be a single vmware-compute node for each vCenter
  - compute-vmware role can not be combined with any other roles
  - The environment must contain at least one KVM/QEMU compute node

Configuration
-------------
To install environment with Contrail and VMWware support you should proceed with following steps:

#. Copy ContrailVM vmdk image to contrail plugin folder on fuel master node

    ::

        scp ContrailVM-disk1.vmdk \
        <Fuel Master node ip>:/var/www/nailgun/plugins/contrail-3.0/

#. Enable contrail plugin in Fuel UI settings

   .. image:: images/enable_contrail_plugin.png

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
