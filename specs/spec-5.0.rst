================================
Fuel Contrail plugin 5.0.0 specs
================================


Provide dedicated DB node for Contrail Analytics
================================================

Problem description
-------------------

Contrail plugin 4.0.1 implements deployment of Contrail analytics services to dedicated nodes with
role 'contrail-analytcics'. In highly scaled environments under load a high amount of analytics data
can be continuously generated, written to and retrieved from Cassandra database, which is shared
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
their manual decommission is not supported, for more details refer to Cassandra documentation [2].
In case if one of Cassandra servers (contrail-analytics-db, contrail-db) become non-operational and
you are planning a replacement, refer to plugin user guide, section 'Restore failed Contrail node'
[3]

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

Contrail with VMware vCenter
============================

Problem description
-------------------
For consolidation under a single administrative control and integration with current VMware vSphere
environment plugin must have possibility to deploy hybrid KVM&VMware OpenStack cloud.

Proposed solution
-----------------
Integration with vCenter include two main roles: compute-vmware and contrail-vmware. As the basis for
compute-vmware role will use default Fuel compute-vmware role. compute-vmware will be located on the
openstack side of hybrid environment and will include nova-compute with Contrail Nova vCenter driver. One
compute-vmware will serve one vCenter. In the current release work with multiple vCenter instances is not
supported. compute-vmware role will be not compatible with any other role. contrail-vmware will be
located on vmware side of hybrid environment and will include Contrail vRouter. One contrail-vmware must
to be installed on each ESXi node. contrail-vmware role will not be compatible with any other role.
Integration assumes that vmware part of the environment already exists - datacenter and clusters are
created. Deployment of the environment will include 2 stages. During the 1st stage user will run script
that prepareS vmware part for deployment (creates few Distributed Switches and spawns virtual machine on
each ESXi node). The rest of management will provided by the Fuel master, more details will be given in
documentation.

UI impact
---------

User must provide credential for vCenter, default Fuel vmware tab will be used for this purpose.
Additionally a few settings need to be added into the Fuel contrail tab. Description of settings
will be given in documentation.

Performance impact
------------------

None

Documentation Impact
--------------------

User guide should be updated with information about this feature.

Upgrade impact
--------------

None

Data model impact
-----------------

None

Other end user impact
---------------------

None

Security impact
---------------

None

Notifications impact
--------------------

None

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
 - Add 'contrail-vmware' role
 - Add manifests that implements 'contrail-vmware' role
 - Add manifests that modify 'compute-vmware' role
 - Write script that will manage vmware environment

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
[3] https://github.com/openstack/fuel-plugin-contrail/blob/master/doc/source/restoring_failed_contrail_node.rst
