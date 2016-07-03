================================
Fuel Contrail plugin 4.0.1 specs
================================


Provide dedicated Contrail Analytics node
=========================================

Problem description
-------------------

Contrail plugin 3.0 implements deployment of Contrail analytics services
in co-location with Contrail config services on the nodes with role
'contrail-config'.
In highly scaled environments under load by thousands of network objects
and instances, a high amount of analytics data can be continiously generated,
causing the high resource usage by contrail-analytics services. That can
negatively impact the performance of contrail-config services running on
the name node.

Proposed solution
-----------------

Create a plugin-defined node role with name 'contrail-analytics' to provide the
possibility to deploy the components of contrail-analytics to a dedicated node or
set of nodes.
The services that should be moved to a dedicated role are Collector, Analytics
API, Query engine, Topology and Alarm generator.
Haproxy configuration should be updated to change the backend addresses to hosts
running analytics services.
This role is mandatory for the contrail-enabled environments, so there must be
at least one node with this role. To achieve high availability the environment
should contain multiple nodes with 'contrail-analytics' role, odd number is
recommended.
The 'contrail-analytics' role can be mixed with other contrail roles
('contrail-db','contrail-config','contrail-control') in small environments,
but not compatible with other OpenStack roles on the same node.
It should be possible to add or remove contrail-analytics nodes after environment
has been deployed.
There is no additional disk space requirements for this role, as analytics
services store the data in Cassandra database. The server hardware requirements is
common for contrail controller nodes.


UI impact
---------

There are no changes in plugin settings tab.
A new role will be available for assigning to slaves in nodes tab.

Performance impact
------------------

Using dedicated nodes for contrail analytics can enhance performance of contrail
config services.

Implementation
==============

Assignee(s)
-----------

Primary assignee:

- Oleksandr Martsyniuk <omartsyniuk> - tech lead, developer
- Vitalii Kovalchuk <vkovalchuk> - developer

Project manager:

- Andrian Noga <anoga>

Quality assurance:

- Oleksandr Kosse <okosse>
- Olesya Tsvigun <otsvigun>

Work items
----------

* Development

 - Update the plugins metadata with 'contrail-analytics' role definition
 - Create new deployment tasks
 - Re-factor the contrail module to ensure that all analytics tasks can be executed
separately
 - Update other manifests to support dedicated analytics nodes
 - Adjust the experimental upgrade scripts to run on contrail-analytics role

* Testing

 - Update tests and test plans to cover new functionality
 - Automation scripts should be updated to deploy environments which contain nodes
with 'contrail-analytics' role

* Documentation

 - User guide should be updated to cover the new roles and features


Acceptance criteria
===================

User can deploy contrail analytics services on node with contrail-analytics role.
Analytics services should be up and running, the status can be verified with
contrail-status command.