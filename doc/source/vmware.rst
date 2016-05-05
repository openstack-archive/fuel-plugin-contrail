Contrail with VMware vCenter
============================

Overview
--------

Starting with Contrail Release 2.20, it is possible to install Contrail to work with the VMware vCenter Server in various vSphere environments.

This topic describes how to install and provision Contrail Release 2.20 and later so that it works with existing or already provisioned vSphere deployments that use openstack as the main orchestrator.

The Contrail VMware vCenter solution is comprised of the following two main components:

Control and management that runs the following components as needed per Contrail system:
A VMware vCenter Server independent installation, that is not managed by Juniper Contrail. The Contrail software provisions vCenter with Contrail components and creates entities required to run Contrail.
The Contrail controller, including the configuration nodes, control nodes, analytics, database, and Web UI, which is installed, provisioned, and managed by Contrail software.
A VMware vCenter plugin provided with Contrail that resides on the compute-vmware node.
VMware ESXi virtualization platforms forming the compute cluster, with Contrail data plane (vRouter) components running inside an Ubuntu-based virtual machine. The virtual machine, named ContrailVM, forms the compute personality while performing Contrail installs. The ContralVM is set up and provisioned by Contrail. There is one ContrailVM running on each ESXi host.
The following figure shows various components of the solution.

    .. image:: images/contrail_vmware_openstack.png

Prerequisites
-------------

   - Installed `Fuel 8.0 <https://docs.mirantis.com/openstack/fuel/fuel-8.0/quickstart-guide.html#introduction>`_
   - Installed contrail plugin :doc:`/install_guide`
   - Environment must be created with "vCenter" support for compute virtualization and "Neutron with tunneling segmentation" for networking
   - vSphere environments must be already preconfigured
   - vCenter server and ESXi hosts must have connection to private network
   - User must provide dhcp server with reservation ip addresses for ContrailVMs. That's mean that you need to bind ip-addresses to mac-addresses for each ContrailVMs.

Restrictions
------------

  - For connection between openstack and vCenter use single host with compute-vmware role (another variants don't tested and probably not works )
  - compute-vmware role can not be combined with any other roles

Configuration
-------------
To install environment with vmware support you should proceed with following steps:

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

#. Check that provisioning of Contrail finished successfully (on primary-controller):

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
  - *Environment type* - this setting was created for development purposes if set "development" ContrailVM will spawn with 2GB RAM otherwise with 8GB.
  - *vCenter Datacenter* - name of vCenter Datacenter
  - *vCenter dvSwitch* - name of vCenter dvSwitch
  - *vCenter DV Port Group* - name of Port Group in vCenter dvSwitch
  - *vCenter DV Port Group number of ports* - number of ports in vCenter Port Group
  - *ntp server for ContrailVM* - ntp server available for ContrailVM
  - *vCenter ESXi data for fabric* - vCenter ESXi data for fabric in YAML format

  **vCenter ESXi data for fabric**
  - on current version of Fuel we don't have possibility to manage ContrailVMs as a separate unit therefore all of manipulation on ContrailVMs are made by fabric scripts from OpenStack primary controller. For fabric purposes user must provide additional data.

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
  - *ip* - ip of esxi where ContrailVM will be spawned
  - *fabric_vswitch* - virtual switch in esxi. This switch will connect ContrailVM(by eth0) with openstack private network
  - *uplink_nic* - name of uplink adapter attached to virtual switch in esxi. Remember that you need to have connectivity with openstack private network.
  - *contrail_vm:mac* - specify mac address of first interface (eth0) in ContrailVM. This setting need for dhcp ip binding.
  - *contrail_vm:host* - user and ip of ContrailVM. This setting will use by fabric for ContrailVM management.
  - *cluster* - name of vCenter cluster
  - *datastore* - path on esxi node where ContrailVM will be store.
