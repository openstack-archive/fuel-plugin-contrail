Contrail TSN (experimental)
===========================


TSN Description
---------------

Contrail supports extending a cluster to include baremetal servers and other
virtual instances connected to a TOR switch supporting OVSDB protocol.
The baremetal servers and other virtual instances can be configured to be part
of any of the virtual networks configured in the contrail cluster, facilitating
communication between them and the virtual instances running in the cluster.
Contrail policy configurations can be used to control this communication.

The solution is achieved by using the OVSDB protocol to configure the TOR switch and
to import dynamically learnt addresses from it. VXLAN encapsulation will be used
in the data plane communication with the TOR switch.

A new node, the TOR services node (TSN), is introduced and provisioned as a new
role in the Contrail system. The TSN acts as the multicast controller for the
TOR switches. The TSN also provides DHCP and DNS services to the bare metal servers
or virtual instances running behind TOR ports.

The TSN receives all the broadcast packets from the TOR, and replicates them to the
required compute nodes in the cluster and to other EVPN nodes. Broadcast packets
from the virtual machines in the cluster are sent directly from the respective
compute nodes to the TOR switch.

The TSN can also act as the DHCP server for the bare metal servers or virtual instances,
leasing IP addresses to them, along with other DHCP options configured in the system.
The TSN also provides a DNS service for the bare metal servers.

.. seealso::

  `Contrail Wiki <https://github.com/Juniper/contrail-controller/wiki/Baremetal-Support>`_

Prerequisites
-------------

This guide assumes that you have installed
`Fuel <http://docs.openstack.org/developer/fuel-docs/userdocs/fuel-user-guide.html>`_
and all the nodes of your future environment are discovered and functional.
To configure TSN in you environment, you need to perform steps additional to :doc:`/install_guide`

To configure TSN in your network, you need TOR switch.

.. raw:: latex

    \clearpage

Configure TSN
-------------

#.  Enable ToR Agents

    .. image:: images/tsn_settings.png

#.  Enable tor agent SSL certifications creation (optional)

#.  Provide Tor Agents configuration in YAML format, based on example
    ::

      01:
        ovs_port: 6286
        ovs_protocol: tcp
        tor_mgmt_ip: 10.109.4.150
        tor_tun_ip: 10.109.4.150
        tor_device_name: ovs1
        tor_vendor_name: ovs
      02:
        ovs_port: 6286
        ovs_protocol: pssl
        tor_mgmt_ip: 10.109.4.151
        tor_tun_ip: 10.109.4.151
        tor_device_name: ovs2
        tor_vendor_name: ovs

#.  Verify working TSN by going to Contrail web UI
