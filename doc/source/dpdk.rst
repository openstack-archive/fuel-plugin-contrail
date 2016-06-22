DPDK-based vRouter
==================

Description
-----------

The Data Plane Development Kit (DPDK) is a set of data plane libraries and network
interface controller drivers for fast packet processing. The DPDK provides a programming
framework for Intel x86 processors and enables faster development of high-speed
data packet networking applications.

By default, Contrail virtual router (vRouter) is running as a kernel module on Linux.

    .. image:: images/vrouter_in_kernelspace.png


The vRouter module can fill a 10G link with TCP traffic from a virtual
machine (VM) on one server to a VM on another server without making any
assumptions about hardware capabilities in the server NICs. Also, to
support interoperability and use a standards-based approach, vRouter does not
use new protocols and encapsulations. However, in network function virtualization
(NFV) scenarios, other performance metrics such as packets-per-second (pps) and
latency are as important as TCP bandwidth. With a kernel module, the pps number
is limited by various factors such as the number of VM exits, memory copies, and
the overhead of processing interrupts.

To optimize performance for NFV use cases, vRouter can be integrated with the Intel DPDK
(Data Plane Development Kit). To integrate with DPDK, vRouter can now run as a user process
instead of a kernel module.

    .. image:: images/vrouter_in_userspace.png


This process links with the DPDK libraries and communicates with the vRrouter host agent,
which runs as a separate process. You can write an application inside of the guest VM to
use the DPDK API or you can use the traditional socket API. However, for NFV applications
such as vMX, which require high performance, using the DPDK API inside the VM is preferable.

Prerequisites
-------------

- Installed `Fuel 8.0 <https://docs.mirantis.com/openstack/fuel/fuel-8.0/>`_
- Installed Contrail plugin :doc:`/install_guide`
- Environment must support ``KVM`` for compute virtualization and ``Neutron with tunneling segmentation`` for networking
- Network card must support DPDK. List of compatible adapters can be found on the
  `DPDK website <http://dpdk.org/doc/guides/nics/index.html>`_

Restrictions
------------

* Only compute hosts can be configured with DPDK role. ``DPDK`` role is just a mark that enables DPDK
  feature on a certain compute node. If you try to use ``DPDK`` role with other roles, ``DPDK`` role
  won't have any effect.

* Contrail DPDK feature doesn't work with qemu virtualization as far as with nested KVM.
  This means that for current release DPDK-based vRouter works only on baremetal computes.

* Contrail DPDK vRouter permanently uses 1GB of hugepages. Therefore, you need to allocate enough
  amount of hugepages to run vRouter and VMs with DPDK.

.. raw:: latex

    \clearpage


Configure DPDK
--------------

To configure DPDK you should proceed with the following steps:

#. Enable the Contrail plugin in Fuel web UI settings

   .. image:: images/enable_contrail_plugin.png

.. raw:: latex

    \pagebreak

2. Enable DPDK on Fuel web UI

   .. image:: images/enable_contrail_dpdk.png

#. Choose the size and amount of huge pages to allocate. They will be used for
   both vRouter process and VMs backing. 2MB sized huge pages can be added on-fly,
   1GB sized require a reboot. Also, leave some amount of memory
   for the operating system itself.

.. raw:: latex

    \pagebreak

4. Add ``DPDK`` role on computes where you want to have DPDK-based vRouter.

   .. note::

      Computes that are not marked with DPDK role will use kernel-based vRouter.

   .. image:: images/add_dpdk_role.png

#. Deploy environment

   .. warning::
      Computes with DPDK-based vRouter require flavor with Huge Pages enabled.
      Instances with usual flavours can't be launched on DPDK-enabled hosts.

   If DPDK is enabled in plugin settings, Fuel will create one flavor that will
   have Huge Pages support, named ``m1.small.hpgs``.
   To create a custom flavor, follow the steps below on the controller node::

    # . openrc
    # nova flavor-create m2.small.hpgs auto 2000 20 2
    # nova flavor-key m2.small.hpgs set hw:mem_page_size=large
    # nova flavor-key m2.small.hpgs set aggregate_instance_extra_specs:hpgs=true

.. raw:: latex

    \clearpage

Verify DPDK
-----------

To verify your installation, proceed with basic checks below:

#. Verify that Contrail services and DPDK vRouter are running on a compute node::

    contrail-status

   **System response**::

    == Contrail vRouter ==
    supervisor-vrouter:           active
    contrail-vrouter-agent        active
    contrail-vrouter-dpdk         active
    contrail-vrouter-nodemgr      active

#. Verify if DPDK vRouter binds network interfaces::

    /opt/contrail/bin/dpdk_nic_bind.py -s

   **Example of system response**::

    Network devices using DPDK-compatible driver
    ============================================
    0000:06:00.0 '82599ES 10-Gigabit SFI/SFP+ Network Connection' drv=igb_uio
    unused=
    Network devices using kernel driver
    ===================================
    0000:02:00.0 'I350 Gigabit Network Connection' if=eth0 drv=igb unused=igb_uio
    0000:02:00.1 'I350 Gigabit Network Connection' if=eth1 drv=igb unused=igb_uio
    0000:06:00.1 '82599ES 10-Gigabit SFI/SFP+ Network Connection' if=eth3 drv=ixgbe   
    unused=igb_uio
    Other network devices
    =====================
    <none>

#. Verify if vRrouter uses Huge Pages::

    grep Huge /proc/meminfo

   **Example of system response**::

    AnonHugePages:         0 kB
    HugePages_Total:   30000
    HugePages_Free:    29488
    HugePages_Rsvd:        0
    HugePages_Surp:        0
    Hugepagesize:       2048 kB


#. Verify if vRouter uses CPU:

    .. image:: images/vrouter_utilize_cpu.png


#. Verify if vRouter creates interface after creation of a virtual machine::

    vif --list

   **Example of system response**::

    Vrouter Interface Table
    Flags: P=Policy, X=Cross Connect, S=Service Chain, Mr=Receive Mirror
           Mt=Transmit Mirror, Tc=Transmit Checksum Offload, L3=Layer 3, L2=Layer 2
           D=DHCP, Vp=Vhost Physical, Pr=Promiscuous, Vnt=Native Vlan Tagged
           Mnp=No MAC Proxy, Dpdk=DPDK PMD Interface, Rfl=Receive Filtering Offload
           Mon=Interface is Monitored, Uuf=Unknown Unicast Flood
           Vof=VLAN insert/strip offload
    vif0/0      PCI: 0:0:0.0 (Speed 10000, Duplex 1)
                Type:Physical HWaddr:00:1b:21:87:21:98 IPaddr:0
                Vrf:0 Flags:L3L2Vp MTU:1514 Ref:14
                RX device packets:3671  bytes:513937 errors:10
                RX port   packets:3671 errors:0
                RX queue  packets:6 errors:0
                RX queue errors to lcore 0 0 0 0 0 0 0 0 0 0 0 0
                RX packets:3671  bytes:499253 errors:0
                TX packets:4049  bytes:2135246 errors:0
                TX port   packets:4049 errors:0
                TX device packets:4049  bytes:2135246 errors:0
    vif0/1      Virtual: vhost0
                Type:Host HWaddr:00:1b:21:87:21:98 IPaddr:0
                Vrf:0 Flags:L3L2 MTU:1514 Ref:8
                RX port   packets:4111 errors:0
                RX queue  packets:4093 errors:0
                RX queue errors to lcore 0 0 0 0 0 0 0 0 0 0 0 0
                RX packets:4111  bytes:2143597 errors:0
                TX packets:3786  bytes:509223 errors:0
                TX queue  packets:790 errors:0
                TX port   packets:3771 errors:0
    vif0/2      Socket: unix
                Type:Agent HWaddr:00:00:5e:00:01:00 IPaddr:0
                Vrf:65535 Flags:L3 MTU:1514 Ref:2
                RX port   packets:45 errors:0
                RX queue errors to lcore 0 0 0 0 0 0 0 0 0 0 0 0
                RX packets:45  bytes:4322 errors:3
                TX packets:951  bytes:95940 errors:0
                TX queue  packets:951 errors:0
                TX port   packets:951 errors:0 syscalls:951
    vif0/3      Ethernet: veth1404577d-b
                Type:Virtual HWaddr:00:00:5e:00:01:00 IPaddr:0
                Vrf:2 Flags:PL3L2D MTU:9160 Ref:11
                RX port   packets:31 errors:0
                RX queue  packets:24 errors:0
                RX queue errors to lcore 0 0 0 0 0 0 0 0 0 0 0 0
                RX packets:31  bytes:18164 errors:0
                TX packets:19  bytes:1091 errors:4
                TX queue  packets:14 errors:0
                TX port   packets:15 errors:0


Change DPDK options
-------------------

This chapter describes how to change DPDK related options from Fuel web UI:

* :guilabel:`Enable DPDK feature for this environment` - this option enables DPDK globally.
  Still you must use ``DPDK`` role to mark a compute node with DPDK

* :guilabel:`Hugepage size` - specifies the size of huge pages that will be used for
  a dpdk feature. Verify if 1GB pages are supported on the target compute node::

   grep pdpe1gb /proc/cpuinfo | uniq

* :guilabel:`Hugepages amount (%)` - sets amount of memory allocated on each compute node for huge pages.
  It will use ``%`` of all memory available on a compute node. DPDK vRouter permanently uses 1GB of huge pages
  and other applications running on compute node may not support huge pages.
  Therefore, use this parameter carefully.

* :guilabel:`CPU pinning` - this hexadecimal value describes how many and which exact processors
  ``dpdk-vrouter`` will use. CPU pinning is implemented using
  `taskset util <http://www.linuxcommand.org/man_pages/taskset1.html>`_

* :guilabel:`Patch Nova` - in the MOS 8.0 release nova doesn't support DPDK-based vRouter.
  In future, MOS maintenance updates will include necessary patches.

* :guilabel:`Install Qemu and Libvirt from Contrail` - DPDK-based vRouter needs
  huge pages memory-backing for guests.
  MOS 8.0 includes qemu and libvirt that don't support huge pages memory-backing.
  DPDK feature needs qemu and libvirt from Contrail only on nodes with ``DPDK`` role.

Change Huge Pages settings after deployment
-------------------------------------------

After deploy is finished, plugin settigs are locked in Fuel web UI.
Therefore, size and ammount of huge pages cannot be changed
by the plugin.
You need to set Huge Pages settings manually on each compute node. 

To set 2MB-sized huge pages:

#. Calculate the number of huge pages based on the ammount you need.
   For example 20GB = 20 * 1024 / 2 = 10240 pages.

#. Set 2MB-sized huge pages::

    sysctl -w vm.nr_hugepages=<number of pages>

#. Edit the ``/etc/sysctl.conf`` file to make these changes persistent over reboots.

On the contrary to setting 2MB-sized huge pages, you can set 1GB-sized huge pages
through the kernel parameter only, which requires a reboot to take effect.
Kernel versions supplied with Ubuntu 14.04 don't support on the fly allocation for 1GB-sized huge pages.

To set 1GB-sized huge pages:

#. Edit the ``/etc/default/grub`` file and set needed amount of huge pages.
   For GRUB_CMDLINE_LINUX in ``/etc/default/grub``::

    GRUB_CMDLINE_LINUX="$GRUB_CMDLINE_LINUX hugepagesz=1024M hugepages=20

#. Update the bootloader and reboot for these parameters to take effect::

    # update-grub
    # reboot
