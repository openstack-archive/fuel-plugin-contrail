==============================
Fuel Contrail plugin 4.0 specs
==============================


Provide deddicated Contrail Analytics node
==========================================

Problem description
-------------------

Contrail plugin 3.0 implements deployment of Contrail analytics services
in co-location with Contrail config services on the nodes with role 
'contrail-config'.
In highly scaled environments under high load, a high amount of analytics data 
can be continiously generated, causing the high resource usage by 
contrail-analytics services. That can negatively impact the performance of
contrail-config services running on the name node.

Proposed solution
------------------

Create a plugin-defined node role with name 'contrail-analytics' to provice the
possibility to deploy the components of contrail-analytics to a dedicated node or 
set of nodes. This role is mandatory for the contrail-enabled environments, so
there must be at least one node with this role. The 'contrail-analytics' role
can be mixed with other contrail roles ('contrail-db','contrail-config',
'contrail-control') in small environments, but not compatible with other 
OpenStack roles on the same node.
There is no addiotional disk space requirements for this role, as analytics
service stores the data in Cassandra database.

UI impact
---------

THere are no changes in plugin settings tab.
A new role will be available for assigning to slaves in nodes tab. 


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

 - Update the plugins metadata with 'contrail-analytics' role definition and
deployment tasks
 - Re-factor the contrail module to ensure that all analytics tasks can be executed
separately, update other manifests to suport dedicated analytics nodes
- Adjust the scripts for contrail packages upgrade

* Testing

 - Update tests and test plans to cover new functionality
 - Automation scripts should be updated to deploy environments which contain nodes
with 'contrail-analytics'. 

* Documentation

 - User guide should be updated to cover the new roles and features

