SRIOV
=====

Prerequisites
-------------

This guide assumes that you have `installed Fuel <https://docs.mirantis.com/openstack/fuel/fuel-7.0/user-guide.html>`_
and performed steps 5.3.1 - 5.3.9 from :doc:`/install_guide`.
To enable SRIOV you need sriov capable network PCI card, with at leats 64 VFs available. Also it is important to remember,
that only compute hosts can be configured with sriov role.


What is SRIOV
-------------

SRIOV is specification which enables one PCI device to appear on computer as multiple physical PCI devices, it provides multiple PFs (Physical Functions) and VFs (Virtual Functions)

How check if network inteface is sriov capable, and how many VFs are available/enabled
--------------------------------------------------------------------------------------

Issue following command on boostraped host::

    lspci -s <bus ID> -vvv

How to enable SRIOV in fuel
---------------------------

#.  Enable SRIOV in plugin settings and configure unique physical name

    .. image:: images/enable_sriov_settings.png
       :width: 80%

#.  Assign SRIOV role to compute hosts

    .. image:: images/enable_sriov_role_node.png
       :width: 80%

#.  Perform deploy as in 5.3.10 :doc:`/install_guide`

How to create VM with sriov device
----------------------------------

#.  Create VN with configured physical network and vlan id::

        neutron net-create --provider:physical_network=<physical network from contrail settings tab> --provider: segmentation_id=<Vlan_id> <Network_Name>

#.  Create a subnet::

        neutron subnet-create <Network_name> <Subnet>

#.  Create a Port::

        neutron port-create --fixed-ip subnet_id=<subnet uuid>,ip_address=<IP address from above subnet> --name <name of port> <vn uuid> --binding:vnic_type direct

#.  Boot VM with the port::

        nova boot --flavor m1.large --image <image name> --nic port-id=<uuid of above port> <vm name>
