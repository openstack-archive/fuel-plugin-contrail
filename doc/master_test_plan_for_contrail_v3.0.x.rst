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


6.1. GUI testing
################

6.1.1. Install Plugin (a)

6.1.2. Check that Contrail UI settings fields are correct  in the Settings tab of the Fuel web UI


6.2. Functional testing
#######################

6.2.1. Deploy a Controller with Plugin (a)

6.2.2. Deploy a Controller node with a Compute node with Plugin (a)

6.2.3. Deploy HA Environment with Plugin (a)(bvt)

6.2.4. Verify HA with assigning public network to all nodes (a)

6.2.5. Verify that it is possible to perform control from nodes after deployment procedure (a)

6.2.6. Check that Contrail Controller node can be added after deploying (a)

6.2.7. Verify deploy Contrail Plugin with vlan tagging (a)

6.2.8. Verify deploy cluster with Networking Templates (a)


6.3. Integration testing
########################

6.3.1. Deploy HA Environment with Contrail

6.3.2. Deploy Environment with  HA-Contrail and Base-OS

6.3.3. Deploy Environment with Contrail and Ceilometer

6.3.4. Deploy Environment with  Contrail and jumbo-frames support

6.3.5. Deploy Environment with  Contrail and vlan tagging


6.4. System testing
###################

6.4.1. Check connectivity between instances placed in a single private network and hosted on different nodes via Contrail network (a)

6.4.2. Check connectivity between instances placed in different private networks and hosted on different nodes (a)

6.4.3. Check connectivity between instances placed in different private networks and hosted on a single node (a)

6.4.4. Check connectivity for instances scheduled on a single compute in a single private network (a)

6.4.5. Check ip and gateway of VMs via Contrail network

6.4.6. Check no connectivity between VMs in different tenants via Contrail network (a)

6.4.7. Check connectivity VMs with external network without floating IP via Contrail network (a)

6.4.8. Create a new network via Contrail WebUI

6.4.9. Check connectivity VMs with external network with floating IP via Contrail network (a)

6.4.10. Testing aggregation of network interfaces (bonding) (a)

6.4.11. Uninstall of plugin (a)

6.4.12. Uninstall of plugin with deployed environment (a)

6.4.13.  Create and terminate networks and verify it in Contrail UI

6.4.14. Deploy cluster with 2 node groups

6.4.15. Verify traffic flow in jumbo-frames-enabled network (a)

6.4.16. Verify connectivity between vms with the same internal ips in different tenants (a)

6.4.17. Launch instance with new security group and check connection after deleting icmp and tcp rules (a)

6.4.18. Check ability to create stacks with contrail-specific atrributes from heat template.


6.5. Failover testing
#####################

6.5.1. Check Contrail HA using network problems (a)

6.5.2. Check Contrail HA using node problems (a)

6.5.3. Enable/disable port to VM (a)

6.5.4. Manual change network settings on instance (a)

6.5.5. Check ssh-connection by floating ip for vm after deleting floating ip

6.5.6. Check can not deploy Contrail cluster with  'contrail_db' only (a)

6.5.7. Check can not deploy Contrail cluster with  'contrail_config' only (a)

6.5.8. Check can not deploy Contrail cluster with  'contrail_control' only (a)

6.5.9. Check can not deploy Contrail cluster with  'contrail_db', 'contrail_config' only (a)

6.5.10. Check can not deploy Contrail cluster with  'contrail_db', 'contrail_control' only (a)

6.5.11. Check can not deploy Contrail cluster with  'contrail_config', 'contrail_control' only (a)

6.5.12. Check Contrail HA with deleting  'contrail_config' (a)

6.5.13. Check Contrail HA with deleting  'contrail_control' (a)

6.5.14. Check Contrail HA with deleting 'contrail_db', 'contrail_config' (a)

6.5.15. Check Contrail HA with deleting 'contrail_db', 'contrail_control' (a)

6.5.16. Check Contrail HA with deleting  'contrail_config', 'contrail_control'(a)
