==============================
Fuel Contrail plugin 3.0 specs
==============================

The Fuel Contrail plugin must be compartible with Mirantis OpenStack 7.0 and the latest Contrail releases targeting OpenStack Kilo.
It uses pluggable architecture enhancements introduced in latest Mirantis OpenStack Fuel.

Reduce the number of cluster networks
=====================================

Problem description
-------------------

Contrail plugin 2.0 uses the network scheme that is standard for Fuel-based deployments
with Neutron with GRE segmentation as network type.
The settings for neutron mesh (private) network are used for configuration of Contrail underlay network.
It is possible to reduce the number of cluster networks using the custom network templates feature,
and assign most of the network roles to the same logical network. Contrail plugin must be aware of
such setup and work properly in case when management, storage and private network roles are assigned
to the same interface.

Reasons
-------
 * Junipers reference architecture suggests using two networks - public and private. It is reasonable to build the environments that match this suggestion using the plugin.
 * Reducing the number of logical networks simplifies the routing within the clusters with multiple L2 segments (racks).

Proposed solution
------------------

Create a reference network templates that includes all internal cluster networks in the same interface.
Make sure that plugin manifests for network configuration are able to create a proper configuration
when custom network template is used for the environment.

::

                                    | Public  | Management
                                    |         | Storage
                                    |         | Private
                                    |         |
    +-------------------------+     |         |
    | Controller              |     |         |
    | +--------------------+  |     |         |
    | | Public VIP         |  +-----+         |
    | |                    |  |               |
    | | Private VIP        |  +---------------+
    | +--------------------+  |               |
    +-------------------------+               |
                                              |
                                              |
                                              |
    +-------------------------+               |
    | Contrail Controller     |               |
    | +--------------------+  |               |
    | | Config             |  |               |
    | | Control            |  +---------------+
    | | Analytics          |  |               |
    | | Database           |  |               |
    | +--------------------+  |               |
    +-------------------------+               |
                                              |
                                              |
    +----------------------------+            |
    |Compute1                    |            |
    |                            +------------+
    |  Contrail vRouter          |            |
    +----------------------------+            |
                                              |
                                              |
    +----------------------------+            |
    |Compute2                    |            |
    |                            +------------+
    |  Contrail vRouter          |            
    +----------------------------+            



Related blueprints
------------------
https://blueprints.launchpad.net/fuel/+spec/templates-for-networking

Define the custom node roles for Contrail components
====================================================

Problem description
-------------------

The Fuel Contrail Plugin version 2.0 makes use of custom user nodes names to select the nodes with base-os role for deployment of Contrail controllers.
This forces to set the mandatory nodes names like 'contrail-1','contrail-2'. This may be complex and to obvious for end users.
Each nodes carries all of contrail components, which is not optimal for large environments, when dedicated database nodes or distributed control nodes may be needed.

Proposed solution
-----------------

Refactor the plugin code to split the code to deploy contrail components to separate puppet tasks, which can be bound to appropriate node roles.
The node roles defined with plugin are:

* contrail-db role. Components  deployed: Cassandra NoSQL database. For this type of nodes, plugin defines a dedicated disk volume type for Cassandra data files, which can be configured with Fuel in nodes disk settings. *Database node role can be combined with other contrail-specific roles.*

* contrail-config role. Components deployed: Zookeeper, IF-MAP, Contrail config, Contrail Analytics, Contrail Web UI. The Web UI, API and Discovery service endpoints will be accessible via custom VIP in Private network on OpenStack controllers. This role All Contrail services use RabbitMQ queue from OpenStack controllers. *Config role can be combined with other contrail roles, such as database.*

* contrail-control role. Components deployed: Contrail Control, Contrail DNS. *This role can be combined with contrail-config and contrail-db roles on the same node.*

Related blueprints
------------------
https://blueprints.launchpad.net/fuel/+spec/role-as-a-plugin

Create Fuel default networks in Contrail on post-deploy
=======================================================

Problem description
-------------------

Contrail-enabled OpenStack environment deployed with plugin version 2.0 has no default networks created.
This is different from traditional deployments, which create the net04 and net04_ext networks. Also these networks
are needed to pass the OSTF tests that are used to verify the environment health. 
So, the end-user has to perform the additional manual steps to create the networks.

Proposed solution
-----------------

Update the plugin with a task, which creates the Fuel default networks after installation of Neutron contrail plugin.
The address range for internal network of admin tenant is defined in Fuel settings, the address range and route target
for external network can be set via plugin settings.  

Implementation
==============

Assignee(s)
-----------

Primary assignee:

- Oleksandr Martsyniuk <omartsyniuk> - tech lead, developer
- Illia Polliul <ipolliul> - developer

Project manager:

- Andrian Noga <anoga>

Quality assurance:

- Oleksandr Kosse <okosse> 
- Iryna Vovk <ivovk>

Work Items
----------

* Create pre-dev environment and manually deploy the latest Contrail software
* Update Fuel plugin bundle to support latest plugin SDK and new features
* Refactor and extend the puppet module

* Test Contrail plugin version 3.0

  - Update tests and test plans to cover new functionality

* Update Documentation

  - Documentation should be updated to cover the new roles and features

