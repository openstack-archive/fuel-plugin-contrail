Installation Guide
==================

Prerequisites
-------------

This guide assumes that you have `installed Fuel <https://docs.mirantis.com/openstack/fuel/fuel-8.0/pdf/Fuel-8.0-UserGuide.pdf>`_
and all the nodes of your future environment are discovered and functional.

Installing Contrail Plugin
--------------------------

#.  Download Contrail plugin from the `Fuel Plugins Catalog <https://software.mirantis.com/download-mirantis-openstack-fuel-plug-ins/>`_.

#.  Copy the rpm downloaded at previous step to the Fuel Master node and install the plugin
    ::

        scp contrail-4.0-4.0.0.noarch.rpm  <Fuel Master node ip>:/tmp/

#.  Log into the Fuel Master node and install the plugin
    ::

        ssh <the Fuel Master node ip>
        fuel plugins --install contrail-4.0-4.0.0.noarch.rpm

    You should get the following output
    ::

        Plugin <plugin-name-version>.rpm was successfully installed

#.  Copy Juniper contrail install package (obtained from Juniper by subscription, more information can be found on
    `official Juniper Contrail web-site <http://www.juniper.net/us/en/products-services/sdn/contrail/contrail-networking/>`_ )
    to the Fuel Master node and run the installation script to unpack the vendor package and populate plugin repository
    ::

        scp contrail-install-packages_3.0.2.0-51~14.04-liberty_all.deb \
        <Fuel Master node ip>:/var/www/nailgun/plugins/contrail-4.0/
        ssh <Fuel Master node ip> /var/www/nailgun/plugins/contrail-4.0/install.sh

.. raw:: latex

    \clearpage


Configuring Contrail Plugin
----------------------------

#.  First, you need to `create environment (page 3) <https://docs.mirantis.com/openstack/fuel/fuel-8.0/pdf/Fuel-8.0-UserGuide.pdf>`_ in Fuel UI.

    .. image:: images/name_and_release.png

#.  Please select KVM or QEMU hypervisor type for your environment

    .. image:: images/compute.png

.. raw:: latex

    \pagebreak

3.  Please select Contrail SDN networking setup.

    .. image:: images/networking_setup.png


#.  If you plan to use Heat orchestration with autoscaling, you need to install Ceilometer too.

    .. image:: images/additional_services.png


#.  Activate the plugin and fill configuration fields with correct values:

    *   AS number for BGP Gateway nodes communication: (defaults to 64512).

    *   Gateway nodes IP addresses (provided as a comma-separated list) - peer addresses for BGP interaction with border routers.

.. raw:: latex

    \pagebreak

6.  Add nodes and assign them the following roles:

    *   At least 1 Controller

    *   At least 1 Compute

    *   At least 1 node with Contrail-Control, Contrail-Config,Contrail-DB roles selected ( 3 or other odd number of nodes
        recommended for HA)

    *   If you plan to use Heat with autoscaling, in addition to Ceilometer you need to add node with MongoDB role

    These 3 roles are not necessary need to be on the same node.
    You can place them on different nodes if needed.

    .. image:: images/contrail-roles.png


    Sample node configuration is provided on a picture below.

    .. image:: images/node-roles.png


#.  The recommended size of partition for Contrail database is 256 GB or more.

#.  Configure the network settings. See details at `Mirantis OpenStack User Guide (page 16) <https://docs.mirantis.com/openstack/fuel/fuel-8.0/pdf/Fuel-8.0-UserGuide.pdf>`_.

    Open "Nodes" tab, select all the nodes and press **Configure interfaces** button

    .. image:: images/conf-interfaces.png


    Set *Private* network to the separate network interface.
    **DO NOT USE THIS PHYSICAL INTERFACE FOR ANY OTHER NETWORK.**
    This interface will be used by contrail vRouter.
    It is recommended to set the bigger MTU for Private interfaces (e.g. 9000) if the switching hardware supports
    Jumbo Frames.
    This will enhance contrail network performance by avoiding packet fragmentation within Private network.

    .. image:: images/public-net.png

    .. warning::

        **First usable addresses from the Private network will be used as VIP for Contrail controllers.**
        For example, if your Private network CIDR is 192.168.200.0/24, then Contrail VIP will be **192.168.200.1**.
        If you want to use other IP as VIP, you need to specify a range for this network.

.. raw:: latex

    \pagebreak

9.  Example network configuration

    Hardware servers with two network interfaces are used as openstack nodes.
    The interfaces configuration is following:

    *   Management and Storage networks on the same interface with Admin net, using tagged VLANs

    *   The second interface is dedicated for Public network as untagged

    *   The forth interface is dedicated for Contrail operations as untagged (Private network)

    .. image:: images/conf-interfaces2.png

    .. warning::
       Be sure to launch `network verification check <https://docs.mirantis.com/openstack/fuel/fuel-7.0/user-guide.html#verify-networks-ug>`_
       before starting deployment. **Incorrect network configuration will result in non-functioning environment.**

#.  Press **Deploy changes** to `deploy the environment (page 25) <https://docs.mirantis.com/openstack/fuel/fuel-8.0/pdf/Fuel-8.0-UserGuide.pdf>`_.

    After installation is finished, `Contrail Web UI <http://www.juniper.net/techpubs/en_US/contrail2.0/topics/task/configuration
    /monitor-dashboard-vnc.html>`_ can be accessed by the same IP address as Horizon, but using HTTPS protocol and port 8143.
    For example, if you configured public network as described on screenshot below, then Contrail Web UI can be accessed by
    **https://<Public-VIP>:8143**

