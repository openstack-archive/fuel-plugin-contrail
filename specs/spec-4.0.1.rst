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
running analytics api [0].
This role is mandatory for the contrail-enabled environments, so there must be
at least one node with this role. To achieve high availability the environment
should contain multiple nodes with 'contrail-analytics' role, odd number is
recommended.
The 'contrail-analytics' role can be mixed with other contrail roles
('contrail-db','contrail-config','contrail-control') in small environments,
but not compatible with other OpenStack roles on the same node.
It should be possible to add or remove contrail-analytics nodes after environment
has been deployed.

UI impact
---------

There are no changes in plugin settings tab.

Performance impact
------------------

Using dedicated nodes for contrail analytics can enhance performance of contrail
config services.

Documentation Impact
--------------------

User guide should be updated with information on new node role.

Upgrade impact
--------------

Experimental scripts for contrail packages upgrade should be updated with
upgrade tasks for 'contrail-analytics' role.

Data model impact
-----------------

None

Other end user impact
---------------------

A new role with name 'contrail-analytics' will be available for assigning to
slaves in nodes tab of Fuel Web UI.

Security impact
---------------

None

Notifications impact
--------------------

None

Requirements
------------

Server requirements are described in [1].
There is no additional disk space requirements for this role, as analytics
services store the data in Cassandra database.



Enable memcache support for contrail keystone middleware
========================================================

Problem description
-------------------

In highly scaled environments under load by thousands of network objects
and instances validating the identity of every client on every request can cost a lot of
computing resources that can produces a big latency in work of Contrail and OpenStack services.
That can negatively impact the performance of whole environment.

Proposed solution
-----------------

Enable caching keystone tokens for Contrail purposes. Similar to `OpenStack approach <http://docs.openstack.org/developer/keystonemiddleware/middlewarearchitecture.html#improving-response-time>`_
Contrail can cache authentication responses from the keystone in memcache. This feature will be enabled by
default and doesn't require any additional settings from Fuel UI. Kyestone middleware will use memcache servers running on OpenStack controllers.

UI impact
---------

There are no changes in plugin settings tab.

Performance impact
------------------

Using caching keystone tokens for Contrail can reduce load of keystone service
respectively enhance performance of Contrail and OpenStack services

Documentation Impact
--------------------

None

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

Requirements
------------

None

Make provisioning of default networks optional
==============================================

Problem description
-------------------

Some environemnts may require changes to default networks created during deployment for OSTF tests.
As an example, network allocated for floating IP addresses may need some exclusions in address
allocation for more-specific routes.
This affects the ability to deploy changes to OpenStack environments, with fails on default
network creation.

Proposed solution
-----------------

Make default networks provisioning optional, and allow manual networks creation.


UI impact
---------
Checkbox for default networks provisioning added. It should be enabled by default.

Performance impact
------------------

None

Documentation Impact
--------------------

User guide should be updated with information about this checkbox.

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

Requirements
------------

None


DPDK-based vRouter feature
==========================

Problem description
-------------------

DPDK (Data Plane Development Kit) allows access to the hardware directly from
applications, bypassing the Linux networking stack (binding interface will not be
seen by the kernel). This reduces latency and allows more packets to be processed.
Plugin need to support installing of Contrail vRouter in this mode.

Proposed solution
-----------------

Create a role called 'DPDK' to mark compute nodes which should be configured to
use DPDK-based vRouter. Hugepages setup must be handled by plug-in, since there's
no hugepages support in Fuel 8.0. For hugepages there should be 2 settings:
type and ammount of pages to allocate. Type has 2 options: 2MB and 1GB.
Ammount should be specified as a percentage from all available memory.
DPDK-based vRouter should use 'Private' interface, in the same way as kernel-based
vRouter does.

DPDK-based vRouter requires some patches to nova-compute, which are not available
in upstream code. Proposed solution is to override Nova packages on Compute nodes
with packages from Contrail distribution. This override should be optional.

DPDK-based vRouter requires VMs to be backed by hugepages. This feature is available
starting from QEMU 2.1, so QEMU and libvirt should be installed from
Contrail distibution. This override should be optional.

UI impact
---------
'DPDK' role should be present in list of roles.
There should be a checkbox that enables DPDK in environment.
Hugepages should have 2 settings: dropdown menu for type and a textfield for ammount.
QEMU and Nova overrides should have checkboxes for toggling this overrides.

Performance impact
------------------

DPDK can be used to increase packet-rate performance on VMs, using DPDK-based
application. With non-DPDK applications performance should be approximately same
as with kernel-based vRouter.

Documentation Impact
--------------------

User guide should be updated with information about usage of this feature.

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

Requirements
------------

Network card on Computes which are selected to use DPDK, should support DPDK.
_`List of supported NICs <http://dpdk.org/doc/nics>`


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

 - Add DPDK role to list of plug-in roles
 - Add checkboxes for DPDK-overrides
 - Add settings for Hugepages
 - Write puppet code for DPDK overrides
 - Write puppet code for Hugepages
 - Create a task for host aggregates and flavors for DPDK
 - Update vRouter configuration for DPDK
 - Update the plugins metadata with 'contrail-analytics' role definition
 - Create new deployment tasks
 - Re-factor the contrail module to ensure that all analytics tasks can be executed separately
 - Update other manifests to support dedicated analytics nodes
 - Adjust the experimental upgrade scripts to run on contrail-analytics role
 - Add python-memcache package to manifests for 'contrail-config' role and adjust the contrail-keystone configuration with memcached server IPs
 - Add checkbox to environment config
 - Make network provisioning conditional

* Testing

 - Update tests and test plans to cover new functionality
 - Automation scripts should be updated to deploy environments which contain nodes with 'contrail-analytics' role

* Documentation

 - User guide should be updated to cover the new roles and features

Acceptance criteria
===================

User can deploy contrail analytics services on node with contrail-analytics role.
Analytics services should be up and running, the status can be verified with
contrail-status command.

References
==========

[0] https://github.com/Juniper/contrail-controller/wiki/Roles-Daemons-Ports
[1] http://www.juniper.net/techpubs/en_US/contrail3.0/topics/task/installation/hardware-reqs-vnc.html
