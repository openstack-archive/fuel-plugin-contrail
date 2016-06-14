DPDK-based vRouter on virtual functions (VF)
============================================

Description
-----------

This guide describe how to run DPDK-based vRouter on virtual functions (VF).
DPDK on VF depend from :doc:`/enable_sriov` and :doc:`/dpdk` features.

Prerequisites
-------------

- Installed `Fuel 8.0 <https://docs.mirantis.com/openstack/fuel/fuel-8.0/quickstart-guide.html#introduction>`_
- Installed Fuel Contrail Plugin :doc:`/install_guide`
- Environment must be created with "KVM" for compute virtualization and "Neutron with tunneling segmentation" for networking
- Network card must support DPDK. List of compatible adapters can be found on `DPDK website <http://dpdk.org/doc/guides/nics/index.html>`_
- Network card must support SRIOV.

How to enable DPDK on VF
------------------------

#. Enable DPDK feature :doc:`/dpdk#configuration`
#. Enable SRIOV feature :doc:`/enable_sriov#how-to-enable-sr-iov-in-fuel`
#. Enable DPDK on VF in Fuel UI settings:

   .. image:: images/enable_dpdk_on_vf.png

#. Assign Compute, DPDK and SRIOV role to the host where you want to enable DPDK on VF feature:

   .. image:: images/compute_dpdk_sriov_roles.png

#. Deploy environment

During deploy on the node with DPDK on VF feature for the private interface will be allocated virtual functions and first VF(dpdk-vf0) will be used for DPDK-based vRouter rest of VFs can be used for nova compute.
