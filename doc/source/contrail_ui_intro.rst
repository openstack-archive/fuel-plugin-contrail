Use Contrail
============

This document describes very basic operations with Contrail UI.

.. seealso::

   `Juniper documentation
   <http://www.juniper.net/techpubs/en_US/contrail2.0/information-products/pathway-pages/getting-started.html#configuration>`_.

.. raw:: latex

   \pagebreak

Log into Contrail
-----------------

To log into Contrail web UI, use the OpenStack admin credentials.

.. image:: images/contrail-login.png

.. raw:: latex

   \pagebreak

Verify services status
----------------------

Verify the status of Contrail Control Analytics and Config nodes along
with vRouters in :guilabel:`Infrastructure` using :guilabel:`Dashboard`
tab of the left-hand :guilabel:`Monitor` menu.

.. image:: images/contrail-services.png


Create the virtual networks
---------------------------

To create the virtual networks:

 *  Open left-hand *Configure* menu and click *Networking* option. Enter :guilabel:`Networks` tab
    and use ``+`` sign at the right side to create a new virtual network.
    Enter the network name and add an IP subnet. Gateway address will be added automatically.

    .. image:: images/contrail-create-net.png

 *  To create an external network, you need to add ``Shared`` and ``External``  flags to the
    created network using the ``Advanced Options`` sections and provide a proper Routing mark
    in Route Targets section to let this network to be announced to the public routing table.
    The Routing mark is two numbers divided by a semicolon, for example ``64512:10000``.

    .. image:: images/contrail-create-ext-net.png

