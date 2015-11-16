================================================
Test Plan for Fuel Contrail plugin version 3.0.x	
================================================	
				
.. contents:: Table of contents
   :depth: 3

************
Introduction
************

Purpose
=======

This document describes Master Test Plan for Contrail v 3.0.x Fuel plugin.
Main purpose of this document is intended to describe Quality Assurance
activities, required to insure that  Contrail v 3.0.x Fuel plugin is  ready for production. 

The scope of this plan defines the following objectives:

* Identify testing activities;
* Outline testing approach, test types, test cycle that will be used;
* List of metrics and deliverable elements;
* List of items for testing and out of testing scope;
* Detect exit criteria in testing purposes;
* Describe test environment.

Scope
=====

The scope of this plan defines the following test types:

* GUI tests
* Functional tests
* Integration tests
* System tests
* Failover tests

Performance testing will be executed on the scale lab and a custom set of rally scenarios must be run with contrail environment. Configuration, enviroment
and scenarios for performance/scale testing should be determined separately.

Intended Audience
=================

This document is intended for project team staff (QA and Dev engineers and
managers) and all other persons who are interested in testing results.

Limitation
==========

Plugin (or its components) has the following limitations:

* Contrail plugin can be enabled only in environments with Neutron gre segmentation as the networking option.
* Deployment of contrail-enabled environment will fail if Base system partition will have less than 256 GB of free space. 


Product compatibility matrix
============================

.. list-table:: product compatibility matrix
   :widths: 15 10 30
   :header-rows: 1

   * - Requirement
     - Version
     - Comment
   * - MOS
     - 7.0 with Kilo
     -
   * - Operating System
     - Ubuntu 14.0.4
     -
   * - Contrail release
     - 3.0

Test environment, infrastructure and tools
==========================================

Following configuration should be used in the testing:

* 3 contrail controllers, 1 controller, 1 compute, Neutron GRE networking with default parameters and installing Contrail plugin 

Other recommendation you can see in the test cases.

**************************************
Evaluation Mission and Test Motivation
**************************************

Project main goal is to build a MOS plugin that integrates a Neutron ML2
Driver For VMWare vCenter DVS. This will allow to use Neutron for networking
in vmware-related environments. The plugin must be compatible with the version
7.0 of Mirantis OpenStack and should be tested with sofware/hardware described
in `product compatibility matrix`_.

See the VMware DVS Plugin specification for more details.

Evaluation mission
==================

* Lab environment deployment.
* Deploy MOS with developed plugin installed.
* Create and run specific tests for plugin/deployment.
* Verify a documentation.

*****************
Target Test Items
*****************

* Install/uninstall Fuel Contrail plugin
* Deploy Cluster with Contrail plugin by Fuel
    * Roles of nodes
        * controller
        * compute
        * cinder
        * mongo
        * contrail controller
    * Storage:
        * Ceph
        * Cinder
    * Network
        * Neutron with GRE segmentation
        * HA + Neutron with GRE
    * Additional components
        * Ceilometer
        * Health Check
 * MOS and Contrail plugin
    * Launch and manage instances 
    * Networks
        * Port binding / disabling
        * Port security
        * Security groups
        * Connection between instances
    * Heat
    * Keystone
        * Create and manage roles
    * Horizon
    * Glance
* GUI
    * Fuel UI
* CLI
    * Fuel CLI
* Contrail UI
* Fuel API
* MOS API

*************
Test approach
*************

The project test approach consists of Smoke,  Integration, System, Regression
Failover and Acceptance  test levels.

**Smoke testing**

Smoke testing is intended to check a correct work of a system after new build delivery.
Smoke tests allow to be sure that all main system functions/features work correctly according to customer requirements.

**Integration and System testing**

The goal of integration and system testing is to ensure that new or modified
components of Fuel and MOS work effectively with Fuel Contrail plugin.

**Regression testing**

Regression testing includes execution of a set of test cases for features implemented before 
current iteration to ensure that following modifications of the system haven’t introduced or uncovered software defects.
It also includes verification of minor defect fixes introduced in the current iteration.

**Failover testing**

Failover and recovery testing ensures that the target-of-test can successfully
failover and recover from a variety of hardware, software, or network
malfunctions with undue loss of data or data integrity.

**Acceptance testing**

The goal of acceptance testing is to ensure that Fuel Contrail plugin has
reached a level of stability that meets requirements  and acceptance criteria.


***********************
Entry and exit criteria
***********************

Criteria for test process starting
==================================

Before test process can be started it is needed to make some preparation
actions - to execute important preconditions. The following steps must be
executed successfully for starting test phase:

* all project requirements are reviewed and confirmed;
* implementation of testing features has finished (a new build is ready for testing);
* implementation code is stored in GIT;
* test environment is prepared with correct configuration, installed all needed software, hardware;
* test environment contains the last delivered build for testing;
* test plan is ready and confirmed internally;
* implementation of manual tests and autotests (if any) has finished.

Feature exit criteria
=====================

Testing of a feature can be finished when:

* All planned tests (prepared before) for the feature are executed; no defects are found during this run;
* All planned tests for the feature are executed; defects found during this run are verified or confirmed to be acceptable (known issues);
* The time for testing of that feature according to the project plan has run out and Project Manager confirms that no changes to the schedule are possible.

Suspension and resumption criteria
==================================

Testing of a particular feature is suspended if there is a blocking issue
which prevents tests execution. Blocking issue can be one of the following:

* Testing environment for the feature is not ready
* Testing environment is unavailable due to failure
* CI test automation scripts failure
* Feature has a blocking defect, which prevents further usage of this feature and there is no workaround available

************
Deliverables
************

List of deliverables
====================

Project testing activities are to be resulted in the following reporting documents:

* Test plan
* Test run report from TestRail
* Automated test cases

Acceptance criteria
===================

* All acceptance criteria for user stories are met.
* All test cases are executed. BVT tests are passed
* Critical and high issues are fixed
* All required documents are delivered
* Release notes including a report on the known errors of that release
* 90% of automation tests should be passed

Such manual tests should be executed and passed (100% of them):

* Create and terminate networks and verify it in Contrail UI;
* Create a new network via Contrail WebUI;
* Deploy cluster with 2 node groups;
* Check ip and gateway of VMs via Contrail network;
* Check that Contrail UI settings fields are correct  in the Settings tab of the Fuel web UI;
* Check ssh-connection by floating ip for vm after deleting floating ip.

**********
Test cases
**********

.. include:: test_suite_functional.rst
.. include:: test_suite_integration.rst
.. include:: test_suite_system.rst
.. include:: test_suite_failover.rst
.. include:: test_suite_gui.rst	