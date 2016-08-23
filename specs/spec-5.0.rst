================================
Fuel Contrail plugin 5.0.0 specs
================================


Provide dedicated DB node for Contrail Analytics
================================================

Problem description
-------------------

Contrail plugin 4.0.1 implements deployment of Contrail analytics services to dedicated nodes with
role 'contrail-analytcics'. In highly scaled environments under load a high amount of analytics data
can be continiously generated, written to and retrieved from Cassandra database, which is shared
with Config and Analytics. That can negatively impact the performance of contrail-config services
the same database. The recommended best practice [0] from Juniper for production deployment of
Contrail is to separate database for Contrail Config and Contrail Analytics. The Contrail Analytics
along with Analytics DB would be installed on a separate node (physical host or VM) while Contrail
Config along with Config DB would be a separate node [0].

Proposed solution
-----------------

Create a plugin-defined node role with name 'contrail-analytics-db' to provide the possibility to
deploy Cassandra for Contrail Analytics to a dedicated node or set of nodes. This role is not
mandatory for the contrail-enabled environments. To achieve high availability the environment should
contain multiple nodes with 'contrail-analytics-db' role, odd number is recommended.
The 'contrail-analytics-db' role can be co-located with 'contrail-analytics', but not compatible
with other OpenStack and Contrail roles on the same node. It should be possible to add
contrail-analytics-db nodes after environment has been deployed. Removing of such nodes without
their manual decomission is not supported, for more details refer to Cassandra documentation [2].

UI impact
---------

A checkbox to enable dedicated Contrail Analytics DB is added to plugin settings.

Performance impact
------------------

Using dedicated nodes for contrail analytics database can enhance performance of contrail services.

Documentation Impact
--------------------

User guide should be updated with information about new node role.

Upgrade impact
--------------

Scripts for contrail packages upgrade should be updated with upgrade tasks for
'contrail-analytics-db' role.

Data model impact
-----------------

None

Other end user impact
---------------------

A new role with name 'contrail-analytics-db' will be available for assigning to slaves in nodes tab
of Fuel Web UI in case if 'Dedicated Analytics DB' plugin setting is turned on.

Security impact
---------------

None

Notifications impact
--------------------

None

Requirements
------------

Server requirements are described in [1]. There are disk space requirements for this role, at least
256 Gb, as analytics services store the data in Cassandra database.

Implementation
==============

Assignee(s)
-----------

Primary assignee:

- Oleksandr Martsyniuk <omartsyniuk> - tech lead, developer
- Vitalii Kovalchuk <vkovalchuk> - developer
- Przemyslaw Szypowicz <pszypowicz> - developer
- Illia Polliul <ipolliul> - developer

Project manager:

- Andrian Noga <anoga>

Quality assurance:

- Oleksandr Kosse <okosse>
- Olesya Tsvigun <otsvigun>

Work items
----------

* Development

 - Add 'Dedicated Analytics DB' to plugin settings
 - Add Contrail Analytics DB role to list of plug-in roles
 - Adjust restrictions for 'contrail-analytics-db' role
 - Refactor contrail-db deployment task to support dedicated DB


* Testing

 - Update tests and test plans to cover new functionality
 - Automation scripts should be updated to deploy environments which contain nodes with
   'contrail-analytics-db' role

* Documentation

 - User guide should be updated to cover the new roles and features

Acceptance criteria
===================

User can deploy DB for Contrail Analytics services on node with contrail-analytics-db role.
Analytics services should be up and running, the status can be verified with
contrail-status command.

References
==========

[0] https://github.com/Juniper/contrail-fabric-utils/wiki/Provisioning-Config-and-Analytics-DB-on-separate-nodes-for-fresh-installation
[1] http://www.juniper.net/techpubs/en_US/contrail3.0/topics/task/installation/hardware-reqs-vnc.html
[2] https://docs.datastax.com/en/cassandra/2.2/cassandra/operations/opsAddingRemovingNodeTOC.html
