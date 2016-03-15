Verification
============
After deploy finishes, you can verify your installation. First proceed with basic checks described below.

Basic checks
------------

#.  Check that Contrail services are running.

    Login to Contrail controller node and run contrail-status command. All services should be in active state:
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

#. Check list of peers and peering status

    Login to Contrail WebUI, go to Monitor -> Control nodes, choose any and select a “Peers” tab. You should see your compute nodes(vRouters) and external router in a list of peers. Status should be “Established”

    .. image:: images/check_list_of_peers.png
       :width: 80%

#. Check that external router was provisioned correctly:

    Login to Contrail WebUI, go to Configure -> Infrastructure -> BGP routers. Verify the IP address of router

    .. image:: images/check_external_router.png
       :width: 80%

    After that you can use health checks in Fuel UI, also called OSTF tests.

OSTF tests
----------

- **Prerequisites for OSTF:**

    #. OSTF tests require two pre-defined networks created - net04 and net04_ext. The networks are created by Fuel during deployment. This section includes instructions how to create them if they where accidentally deleted. Floating IP addresses from net04_ext should be accessible from Fuel master node.
    #. 3 tests from “Functional tests” set require floating IP addresses. They  should be configured on external router, routable from Fuel master node and     populated in Contrail/Openstack environment.
    #. HA tests require at least 3 Openstack controllers.
    #. “Platform services functional tests.” require Ceilometer and Mongo.

- **OSTF networks and floating IPs configuration:**

    To create networks go to Contrail WebUI -> Configure -> Networking -> Networks
    
    #. Create network “net04”
    
        .. image:: images/create_network_net04.png
           :width: 80%
    
    #. Create network “net04_ext”.
    
        .. image:: images/create_network_net04_ext.png
           :width: 80%
    
        It should be marked as “shared” and “external”
    
        .. image:: images/create_network_net04_ext2.png
            :width: 80%
    
        And have same route target as configured in external router
    
        .. image:: images/create_network_net04_ext3.png
           :width: 80%
    
    #. Allocate floating IP addresses from net04_ext
    
        Go to Contrail WebUI --> Configure -> Networking -> Manage Floating IPs
    
        .. image:: images/allocate_floating_ip_addresses.png
           :width: 80%

After configuring networks and floating IP addresses, start OSTF tests. For more details, refer to `Fuel user-guide <https://docs.mirantis.com/openstack/fuel/fuel-7.0/user-guide.html#post-deployment-check>`_.
