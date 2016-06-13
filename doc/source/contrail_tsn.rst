Contrail TSN
============

Prerequisites
-------------

This guide assumes that you have `installed Fuel <https://docs.mirantis.com/openstack/fuel/fuel-7.0/user-guide.html>`_
and all the nodes of your future environment are discovered and functional.
To configure TSN in you environment you need to perform steps additional to :doc:`/install_guide`

To configure TSN in your network you will need TOR switch.

What is TSN
-----------

A new node, the TOR services node (TSN), is introduced and provisioned as a new role in the Contrail system. The TSN acts as the multicast controller for the TOR switches. The TSN also provides DHCP and DNS services to the bare metal servers or virtual instances running behind TOR ports.

The TSN receives all the broadcast packets from the TOR, and replicates them to the required compute nodes in the cluster and to other EVPN nodes. Broadcast packets from the virtual machines in the cluster are sent directly from the respective compute nodes to the TOR switch.

The TSN can also act as the DHCP server for the bare metal servers or virtual instances, leasing IP addresses to them, along with other DHCP options configured in the system. The TSN also provides a DNS service for the bare metal servers. Multiple TSN nodes can be configured in the system based on the scaling needs of the cluster.

Configuring TSN
---------------

#.  Enable ToR Agents

    .. image:: images/tsn_settings.png
       :width: 80%

#.  Enable tor agent SSL certifications creation (optional)

#.  Provide Tor Agents configuration in YAML format, based on example

#.  Verify working TSN by going to contrail WebUI