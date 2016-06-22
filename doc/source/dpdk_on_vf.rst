DPDK-based vRouter on virtual function (VF) (experimental)
==========================================================

Description
-----------

This guide describes how to run DPDK-based vRouter on virtual functions (VF).
DPDK on VF depends on :doc:`/enable_sriov` and :doc:`/dpdk` features.
This feature shares a physical interface for DPDK and SR-IOV usage.

Prerequisites
-------------

- Installed `Fuel 8.0 <http://docs.openstack.org/developer/fuel-docs/userdocs/fuel-user-guide.html>`_
- Installed Fuel Contrail Plugin :doc:`/install_guide`
- Environment must be created with "KVM" for compute virtualization and "Contrail" for networking
- Network card must support DPDK.
  List of compatible adapters can be found on `DPDK website <http://dpdk.org/doc/guides/nics/index.html>`_
- Network card must support SRIOV.

How to enable DPDK on VF
------------------------

#. Enable DPDK feature :doc:`/dpdk`.
#. Enable SRIOV feature :doc:`/enable_sriov`.
#. Enable DPDK on VF in Fuel UI settings:

   .. image:: images/enable_dpdk_on_vf.png

#. Assign ``Compute``, ``DPDK``, and ``SRIOV`` roles to the host where you want to enable DPDK on VF feature:

   .. image:: images/compute_dpdk_sriov_roles.png

#. Deploy environment

If DPDK on VF is enabled in plugin settings, it will be deployed on computes with ``DPDK``
and ``SR-IOV`` roles.
During deploy following configurations will be made on compute nodes with DPDK and SR-IOV roles:

  #. Virtual functions will be allocated on private interface.
  #. First VF (dpdk-vf0) will be used for DPDK-based vRouter.
  #. Rest of the VFs will be added to ``pci_passthrough_whitelist`` setting in ``nova.conf``
     for SR-IOV usage.
