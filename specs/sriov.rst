Enable SRIOV functionality via plugin
=====================================

Problem description
-------------------

Contrail plugin enables possibility to use SRIOV. We need to develop SRIOV support
in fuel contrail plugin

Proposed solution
-----------------

Adding sriov to openstack contrail deployment, will need actions mostly on compute node.
We have to add users possibility to deploy compute node as sriov host, and then configure
several options there. This will consist of grub changes, nova.conf, reconfiguring interfaces.

UI impact
---------

In settings tab you will have to enable sriov support. On nodes tab you will have to assign SRIOV role
to compute nodes which will need sriov support.

Performance impact
------------------

Using sriov can effect in lower latency and near-line wire speed.

Documentation Impact
--------------------

User guide should be updated with information on new node role.

Upgrade impact
--------------

---

Data model impact
-----------------

None

Other end user impact
---------------------

A new role with name 'sriov' will be available for assigning to
compute slaves in nodes tab of Fuel Web UI.

Security impact
---------------

None

Notifications impact
--------------------

None

Requirements
------------

Compute servers are expected to have network cards cappable of sriov functionality