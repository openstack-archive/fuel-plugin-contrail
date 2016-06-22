Verify Contrail plugin
======================

To verify your installation after deployment, perform the basic checks described below.

#.  Verify that Contrail services are running.

    #. Login to the Contrail controller node and run ``contrail-status`` command.
       All services should be in "active" state:
       ::

        # contrail-status
            == Contrail Control ==
            supervisor-control:           active
            contrail-control              active
            contrail-control-nodemgr      active
            contrail-dns                  active
            contrail-named                active

            == Contrail Analytics ==
            supervisor-analytics:         active
            contrail-analytics-api        active
            contrail-analytics-nodemgr    active
            contrail-collector            active
            contrail-query-engine         active
            contrail-snmp-collector       active
            contrail-topology             active

            == Contrail Config ==
            supervisor-config:            active
            contrail-api:0                active
            contrail-config-nodemgr       active
            contrail-device-manager       active
            contrail-discovery:0          active
            contrail-schema               active
            contrail-svc-monitor          active
            ifmap                         active

            == Contrail Web UI ==
            supervisor-webui:             active
            contrail-webui                active
            contrail-webui-middleware     active
            == Contrail Database ==
            supervisor-database:          active
            contrail-database             active
            contrail-database-nodemgr     active
            kafka                         active

#. Verify the list of peers and peering status

   #. Login to Contrail web UI
   #. Go to :guilabel:`Monitor -> Control nodes`
   #. Choose any and select a :guilabel:`Peers` tab.
      You should see your compute nodes (vRouters) and external router
      in a list of peers with status ``Established``

    .. image:: images/check_list_of_peers.png


#. Verify that external router has been provisioned correctly:

    #. Login to Contrail web UI
    #. Go to :guilabel:`Configure -> Infrastructure -> BGP routers`.
    #. Verify the IP address of the router

    .. image:: images/check_external_router.png


    #. Use health checks in Fuel web UI, also called OSTF tests.

Run OSTF tests
--------------

Prerequisites for OSTF
++++++++++++++++++++++

    #. OSTF tests require two pre-defined networks created - ``net04`` and ``net04_ext``.
       The networks are created by Fuel during deployment. This section includes
       instructions how to create them if they were accidentally deleted. Floating
       IP addresses from net04_ext should be accessible from Fuel master node.
    #. Three tests from ``Functional tests`` set require floating IP addresses.
       They  should be configured on external router, routable from Fuel master node and
       populated in the Openstack with Contrail environment.
    #. HA tests require at least three Openstack controllers.
    #. ``Platform services functional tests.`` require Ceilometer and MongoDB.

Configure OSTF networks and floating IPs
++++++++++++++++++++++++++++++++++++++++

To configure OSTF networks and floating IPs:

#. Go to Contrail web UI :guilabel:`Configure -> Networking -> Networks`

#. Create network ``net04``

        .. image:: images/create_network_net04.png


#. Create network ``net04_ext``.

   .. image:: images/create_network_net04_ext.png

   It should be marked as ``shared`` and ``external``

   .. image:: images/create_network_net04_ext2.png

   And have same route target as configured in an external router

   .. image:: images/create_network_net04_ext3.png


#. Allocate floating IP addresses from ``net04_ext``

   #. Go to Contrail WebUI :guilabel:`Configure -> Networking -> Manage Floating IPs`

      .. image:: images/allocate_floating_ip_addresses.png


#. Start OSTF tests.

.. seealso::

   `Fuel user-guide <http://docs.openstack.org/developer/fuel-docs/userdocs/fuel-user-guide/verify-environment/intro-health-checks.html>`_.

Troubleshooting
---------------

To troubleshoot:

#. Verify output of the ``contrail-status`` command.
#. Verify the logs for corresponding serivice:

   * Contrail logs are located in ``/var/log/contrail/`` directory, and log names match with contrail service name.
   * Cassandra logs are located in  ``/var/log/cassandra/``
   * Zookeeper logs are in ``/var/log/zookeeper/``
