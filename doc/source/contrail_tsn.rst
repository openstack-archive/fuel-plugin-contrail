Contrail TSN
============


TSN Description
---------------

Contrail supports extending a cluster to include bare metal servers and other
virtual instances connected to a TOR switch supporting OVSDB protocol.
You can configure the bare metal servers and other virtual instances to be a part
of any of the virtual networks configured in the contrail cluster facilitating
communication between them and the virtual instances running in the cluster.
You can use Contrail policy configurations to control this communication.

The solution uses the OVSDB protocol to configure the TOR switch and
to import dynamically learnt addresses from it. VXLAN encapsulation will be used
in the data plane communication with the TOR switch.

A new node, the TOR services node (TSN), is introduced and provisioned as a new
role in the Contrail system. The TSN acts as the multicast controller for the
TOR switches. TSN also provides DHCP and DNS services to the bare metal servers
or virtual instances running behind TOR ports.

TSN receives all the broadcast packets from the TOR, and replicates them to the
required compute nodes in the cluster and to other EVPN nodes.  Broadcast packets
from the virtual machines in the cluster are sent directly from the respective
compute nodes to the TOR switch.

TSN can also act as the DHCP server for the bare metal servers or virtual instances,
leasing IP addresses to them, along with other DHCP options configured in the system.
TSN also provides a DNS service for the bare metal servers.

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

HA implementation details
-------------------------

Contrail TSN in HA mode is implemented for default SSL mode.

All required certificates will be located on CONTRAIL-TSN node in location:
::

  /var/lib/astute/tsn_certificates/certs

There will be two folders per TOR service. Folder named tor_agent_<@id> contain certs
for tor agent service. Folder named vtep_<@id> contain certificates which should be delivered
to ToR Switch.

Configure TSN
-------------

#.  Enable ToR Agents

    .. image:: images/tsn_settings.png

#.  Provide Tor Agents configuration in YAML format, based on example
    ::

      01:
        tor_mgmt_ip: 10.109.4.150
        tor_tun_ip: 10.109.4.150
        tor_device_name: ovs1
        tor_vendor_name: ovs
      02:
        tor_mgmt_ip: 10.109.4.151
        tor_tun_ip: 10.109.4.151
        tor_device_name: ovs2
        tor_vendor_name: ovs

#.  Deploy additional node/nodes with CONTRAIL-TSN role

    .. image:: images/contrail-tsn-nodes.png

#.  Configure ToR Switches with SSL certificates located on TSN node in:
    ::

      /var/lib/astute/tsn_certificates/certs

#.  Verify working TSN by going to Contrail web UI
