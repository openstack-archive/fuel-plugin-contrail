..
 This work is licensed under a Creative Commons Attribution 3.0 Unported
 License.

 http://creativecommons.org/licenses/by/3.0/legalcode

==========================================
Fuel Plugin for Contrail SDN intgration
==========================================

Contrail plugin for Fuel provides the functionality to add Сontrail SDN for Mirantis OpenStack as networking backend option.

It uses Fuel plugin architecture.
The plugin must be compatible with  the  version 6.1 of Mirantis OpenStack and Contrail 2.0.
Only HA mode for MOS and Contrail controllers supported. It will be allowed to deploy an only Contrail Controller (for test-bed environments) and add more controllers later (to add true HA).
Contrail LBaaS feature can be enabled.

Problem description
===================


Proposed change
===============

Implement a Fuel plugin which will deploy Contrail SDN controllers and configure MOS to use Contrail instead of Neutron.

Alternatives
------------

It also might be implemented as a part of FUEL core, but we decided to make it as a plugin for several reason:
* Any new additional functionality makes a project and testing more difficult, which is an additional risk for the FUEL release.

Data model impact
-----------------

REST API impact
---------------

Upgrade impact
--------------

Fuel currently supports upgrading of master node, so it is necessary to install a new version of plugin which supports new Fuel release.

Security impact
---------------

Notifications impact
--------------------

Other end user impact
---------------------

Contrail plugin uses Fuel pluggable architecture.
After it was installed, the user can enable the plugin in Setting tab and customize plugins settings.

Performance Impact
------------------

Other deployer impact
---------------------

Developer impact
----------------

Implementation
==============

Assignee(s)
-----------

Feature lead: Oleksandr Martsyniuk
Developers: Vyacheslav Struk
QA: Oleksandr Kosse, Iryna Vovk


Work Items
----------

* Create pre-dev environment and manually deploy Contrail software
* Implement FUEL plugin.
* Implement puppet manifests.
* Testing.
* Create Documentation.


Dependencies
============

* Fuel 6.1 and higher.

Testing
=======


Documentation Impact
====================

* Deployment Guide (how to prepare an env for installation, how to install the plugin, how to deploy OpenStack env with the plugin).	1
* User Guide (which features the plugin provides, how to use them in the deployed OS env).
* Test Plan.
* Test Report.

References
==========

* Fuel Plug-in Guide http://docs.mirantis.com/openstack/fuel/fuel-6.0/plugin-dev.html
* Fuel plugins: consolidated document https://docs.google.com/a/mirantis.com/document/d/1K9bwUMT-afnpFr9bND_WORKopeB7fLQfzl4-gDsl6VM
* Contrail plugin proposal https://docs.google.com/a/mirantis.com/document/d/1lvhLGutVQ1L-MzX78FxPQ89f0m1MZbDF1h2fMfQ-Mf4
* Juniper OpenContrail integration with Fuel
 - https://docs.google.com/a/mirantis.com/document/d/1zktTAy0JaR7Z28OB9ac9GY_NVOCgSv2D-tx-Q7Y80Jo
 - https://docs.google.com/a/mirantis.com/document/d/1TxnKF-74cbcEdCQFt14QnM5STaZHLfmWzmItirR3IMM/edit
* Juniper Networks TechWiki > Documentation > Contrail http://techwiki.juniper.net/Documentation/Contrail
* Advanced Networking feature in Fuel https://blueprints.launchpad.net/fuel/+spec/advanced-networking 


