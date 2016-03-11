=================================================
Master Test Plan for Contrail v 3.0.x Fuel Plugin
=================================================


1. Introduction
---------------


1.1. Purpose
############

This document describes Master Test Plan for Contrail v 3.0.x Fuel Plugin. The scope of this plan defines the following objectives:

* describe testing activities;
* outline testing approach, test types, test cycles that will be used;
* test mission;
* deliverables;


1.2. Intended Audience
######################

This document is intended for Contrail project team staff (QA and Dev engineers and managers) all other persons who are interested in testing results.


2. Governing Evaluation Mission
-------------------------------

Contrail plugin for Fuel provides the functionality to add Сontrail SDN for Mirantis OpenStack as networking backend option.

It uses Fuel plugin architecture along with pluggable architecture enhancements introduced in latest Mirantis OpenStack Fuel.

The plugin must be compatible with  the  version 7.0 of Mirantis OpenStack and Contrail release 3.0.x.
It will be allowed to deploy an only Contrail Controller (for test-bed environments) and add more controllers later (to add true HA).

See Contrail Plugin 3.0.x Proposal for more details


2.1. Evaluation Test Mission
############################

* Lab environment deployment.
* Deploy MOS with developed plugin installed.
* Create and run specific tests for plugin/deployment.
* Documentation


2.2.  Test Items
################

* Contrail UI;
* Fuel CLI;
* Fuel API;
* Fuel UI;
* MOS;
* MOS UI;
* MOS API.


3. Test Approach
----------------

The project test approach consists of BVT, Integration/System, Regression and Acceptance test levels.


3.1. Criterias for test process starting
########################################

Before test process can be started it is needed to make some preparation actions - to execute important preconditions.
The following steps must be executed successfully for starting test phase:

* all project requirements are reviewed and confirmed;
* implementation of testing features has finished (a new build is ready for testing);
* implementation code is stored in GIT;
* bvt-tests are executed successfully (100% success);
* test environment is prepared with correct configuration;
* test environment contains the last delivered build for testing;
* test plan is ready and confirmed internally;
* implementation of manual tests and necessary autotests has finished.


3.2. Suspension Criteria
########################

Testing of a particular feature is suspended if there is a blocking issue which prevents tests execution. Blocking issue can be one of the following:

* Feature has a blocking defect, which prevents further usage of this feature and there is no workaround available;
* CI test automation scripts failure.


3.3. Feature Testing Exit Criteria
##################################

Testing of a feature can be finished when:

* All planned tests (prepared before) for the feature are executed; no defects are found during this run;
* All planned tests for the feature are executed; defects found during this run are verified or confirmed to be acceptable (known issues);
* The time for testing of that feature according to the project plan has run out and Project Manager confirms that no changes to the schedule are possible.


4. Deliverables
---------------


4.1 List of deliverables
########################

Project testing activities are to be resulted in the following reporting documents:

* Test plan;
* Test run report from TestRail;


4.2. Acceptance criterias
#########################

90% of automation tests should be passed. Critical and high issues are fixed.
Such manual tests should be executed and passed (100% of them):

* Create and terminate networks and verify it in Contrail UI;
* Create a new network via Contrail WebUI;
* Deploy cluster with 2 node groups;
* Check ip and gateway of VMs via Contrail network;
* Check that Contrail UI settings fields are correct  in the Settings tab of the Fuel web UI;
* Check ssh-connection by floating ip for vm after deleting floating ip.


5. Test Cycle Structure
-----------------------

An ordinary test cycle for each iteration consists of the following steps:

* Smoke testing of each build ready for testing;
* Verification testing of each build ready for testing;
* Regression testing cycles in the end of iteration;
* Creation of a new test case for covering of a new found bug (if such test does not exist).


5.1.1 Smoke Testing
###################

Smoke testing is intended to check a correct work of a system after new build delivery. Smoke tests allow to be sure that all main system functions/features work correctly according to customer requirements.


5.1.2 Verification testing
##########################

Verification testing includes functional testing covering the following:

* new functionality (implemented in the current build);
* critical and major defect fixes (introduced in the current build).

Some iteration test cycles also include non-functional testing types described in Overview of Planned Tests.


5.1.3 Regression testing
########################

Regression testing includes execution of a set of test cases for features implemented before current iteration to ensure that following modifications of the system haven't introduced or uncovered software defects.
It also includes verification of minor defect fixes introduced in the current iteration.


5.1.4 Bug covering by new test case
###################################

When test cases are written (manual or automated) and testing process has been started bugs are starting to be detected. Ideally, each bug must be found by a prepared test case. But sometimes some bug has been occurred without corresponding test coverage (reasons are too many). In this situation if someone has found a bug and there is no a corresponding test case in the system it is very important to implement a special test case for preventing this bug occurring in the future. New test cases must be added into TestRail (if we speak about manual test) and a corresponding autotest must be implemented and storage in a Git/Gerrit repo.


5.2 Performance testing
#######################

Performance testing will be executed on the scale lab and a custom set of rally scenarios must be run with contrail environment.


5.3 Metrics
###########

Test case metrics are aimed to estimate a quality of bug fixing; detect not running tests and plan their execution.
Passed / Failed test cases - this metric shows results of test cases execution, especially, a ratio between test cases passed successfully and failed ones. Such statistics must be gathered after testing of each delivered build. This will help to identify a progress in successful bugs fixing. Ideally, a count of failed test cases should aim to a zero.

Not Run test cases - this metric shows a count of test cases which should be run within a current test phase (have not run yet). Having such statistics, there is an opportunity to detect and analyze a scope of not run test cases, causes of their non execution and planning of their further execution (detect time frames, responsible QA).


6. Test scope
-------------

.. include:: test_suite_smoke_bvt.rst
.. include:: test_suite_integration.rst
.. include:: test_suite_functional.rst
.. include:: test_suite_failover.rst
.. include:: test_suite_gui.rst
.. include:: test_suite_system.rst
.. include:: test_suite_sriov.rst
