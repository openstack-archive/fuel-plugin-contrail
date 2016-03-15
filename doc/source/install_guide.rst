Installation Guide
==================

Prerequisites
-------------

This guide assumes that you have `installed Fuel <https://docs.mirantis.com/openstack/fuel/fuel-7.0/user-guide.html>`_
and all the nodes of your future environment are discovered and functional.
Note, if you want to use Juniper Contrail instead of OpenContrail, you need to get proprietary Contrail packages
for your operating system.
They can be obtained from Juniper as a part of your support subscription.
OpenContrail packages are provided within the plugin package.

Installing Contrail Plugin
--------------------------

#.  Download Contrail plugin from the `Fuel Plugins Catalog <https://software.mirantis.com/download-mirantis-openstack-fuel-plug-ins/>`_.
#.  Copy the rpm downloaded at previous step to the Fuel Master node and install the plugin:
    ::

        scp contrail-3.0-3.0.0-1.noarch.rpm  <Fuel Master node ip>:/tmp/

#.  Log into the Fuel Master node and install the plugin
    ::

        ssh <the Fuel Master node ip>
        fuel plugins --install /tmp/contrail-3.0.0.noarch.rpm

    You should get the following output
    ::

        Plugin <plugin-name-version>.rpm was successfully installed

#.  In case if you are using Juniper Contrail, copy Juniper contrail install package (obtained from Juniper by subscription, see Prerequisites above) to the Fuel Master node and run the installation script to unpack the vendor package and populate plugin repository
    ::

        scp contrail-install-packages_3.0-2652-kilo_all.deb \
        <Fuel Master node ip>:/var/www/nailgun/plugins/contrail-3.0/
        ssh <Fuel Master node ip> /var/www/nailgun/plugins/contrail-3.0/install.sh

.. raw:: latex

   \pagebreak

Configuring Contrail Plugin
---------------------------

#.  First you need to `create environment <https://docs.mirantis.com/openstack/fuel/fuel-7.0/user-guide.html#create-a-new-openstack-environment>`_ in Fuel UI.

    .. image:: images/name_and_release.png
       :width: 80%

#.  Please select KVM or QEMU hypervisor type for your environment

    .. image:: images/compute.png
       :width: 80%

#.  Please select Neutron with tunneling segmentation network model.
    GRE segmentation is also supported, but you need to set it from Fuel CLI

    .. image:: images/networking_setup.png
       :width: 80%

#.  If you plan to use Heat orchestration with autoscaling, you need to install Ceilometer too.

    .. image:: images/additional_services.png
       :width: 80%

#.  Activate the plugin and fill configuration fields with correct values:

    *   Select the Contrail packages distribution: OpenContrail from plugin package or proprietary Contrail packages
        from Juniper.

    *   AS number for BGP Gateway nodes communication: (defaults to 64512).

    *   Gateway nodes IP addresses (provided as comma-separated list) - peer addresses for BGP interaction with border routers.

#.  Add nodes and assign them the following roles:

    *   At least 1 Controller

    *   At least 1 Compute

    *   At least 1 node with Contrail-Control, Contrail-Config,Contrail-DB roles selected ( 3 or other odd number of nodes
        recommended for HA)

    *   If you plan to use Heat with autoscaling, in addition to Ceilometer you need to add node with MongoDB role

    This 3 roles are not necessary need to be on same node.
    You can place them on different nodes if needed.

    .. image:: images/contrail-roles.png
       :width: 80%

    Sample node configuration is provided on picture below.

    .. image:: images/node-roles.png
       :width: 80%

#.  `Configure the disks <https://docs.mirantis.com/openstack/fuel/fuel-master/user-guide.html#id46>`_ on nodes with
    Contrail-DB role selected.
    The recommended size of partition for Contrail database is 256 GB or more.

#.  Configure the network settings. See details at `Mirantis OpenStack User Guide <https://docs.mirantis.com/
    openstack/fuel/fuel-7.0/user-guide.html#network-settings-ug>`_.

    *   Open Nodes tab:
        Select all the nodes, push **Configure interfaces** button

        .. image:: images/conf-interfaces.png
           :width: 80%

    *   Set *Private* network to the separate network interface as untagged network.
        **DO NOT USE THIS PHYSICAL INTERFACE FOR ANY OTHER NETWORK.**
        This interface will be used by contrail vRouter as untagged port.
        It is recommended to set set the bigger MTU for Private interfaces (e.g. 9000) if the switching hardware supports
        Jumbo Frames.
        This will enhance contrail network performance by avoiding packet fragmentation within Private network.


    For other networking options please refer to `Mirantis OpenStack User Guide <https://docs.mirantis.com/openstack/fuel
    /fuel-7.0/user-guide.html#network-settings-ug>`_.
    In case of using multiple L2 segments you may need to configure networking according to the `Operations Guide
    <https://docs.mirantis.com/openstack/fuel/fuel-7.0/operations.html#configuring-multiple-cluster-networks>`_ and supply
    static routes to BGP peers and other cluster networks in network_1.yaml file.

#.  Example network configuration

    Hardware servers with two network interfaces are used as openstack nodes.
    The interfaces configuration is following:

    *   Public, Management and Storage networks on the same interface with Admin net, using tagged VLANs

    *   Second interface is dedicated for Contrail operations as untagged (Private network)

    .. image:: images/conf-interfaces2.png


#.  Press **Deploy changes** to `deploy the environment <https://docs.mirantis.com/openstack/fuel/fuel-7.0/user-guide.html#
    deploy-changes>`_.

    After installation is finished, `Contrail Web UI <http://www.juniper.net/techpubs/en_US/contrail2.0/topics/task/configuration
    /monitor-dashboard-vnc.html>`_ can be accessed by the same IP address as Horizon, but using HTTPS protocol and port 8143.
    For example, if you configured public network as described on screenshot below, then Contrail Web UI can be accessed by
    **https://172.16.0.2:8143**

    .. image:: images/public-net.png

    .. note::

        WARNING! first usable addresses from Private network will be used as VIP for Contrail controllers.
        For example, if your Private network CIDR is 192.168.200.0/24, then Contrail VIP will be **192.168.200.1**.
