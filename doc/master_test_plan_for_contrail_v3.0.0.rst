

=================================================
Master Test Plan for Contrail v 3.0.0 Fuel Plugin
=================================================

--------------
1. GUI testing
--------------

1.1 Install Plugin (a)

1.2 Check that Contrail UI settings fields are correct  in the Settings tab of the Fuel web UI

---------------------
2. Functional testing
---------------------

2.1 Deploy a Controller with Plugin (a)

2.2 Deploy a Controller node with a Compute node with Plugin (a)

2.3 Deploy HA Environment with Plugin (a)(bvt)

2.4 Verify HA with assigning public network to all nodes (a)

2.5 Verify that it is possible to perform control from nodes after deployment procedure (a)

2.6 Check that Contrail Controller node can be added after deploying (a)

2.7 Verify deploy Contrail Plugin with vlan tagging (a)

2.8 Verify deploy cluster with Networking Templates (a)

----------------------
3. Integration testing
----------------------

3.1 Check VM migration on Compute (a)

3.2 Check that Controller node can be deleted and added again (a)(bvt)

3.3 Check that Compute node can be deleted and added again (a)(bvt)

3.4 Deploy Contrail cluster with Ceph on Compute nodes (a)

3.5 Deploy Contrail cluster with Ceilometer (a)

3.6 Deploy Contrail cluster with jumbo frames enabled for Private network (a)

3.7 Deploy Contrail cluster with three contrail roles on one node (a)

3.8 Deploy Contrail cluster with three contrail roles on three different nodes (a)

3.9 Verify that ‘contrail_config’ role can be deleted and added back to the cluster (a)

3.10 Verify that ‘contrail_control’ role can be deleted and added back to the cluster (a)

3.11 Deploy ‘contrail_db’ on one node and ‘contrail_config’, ‘contrail_control’ on other node (a)

3.12 Deploy ‘contrail_db’, ‘contrail_config’ on one node and ‘contrail_control’ on other node (a)

3.13 Deploy ‘contrail_config’ on one node and  ‘contrail_db’, ‘contrail_control’ on other node (a)

-----------------
4. System testing
-----------------

4.1 Check connectivity between instances placed in a single private network and hosted on different nodes via Contrail network (a)

4.2 Check connectivity between instances placed in different private networks and hosted on different nodes (a)

4.3 Check connectivity between instances placed in different private networks and hosted on a single node (a)

4.4 Check connectivity for instances scheduled on a single compute in a single private network (a)

4.5 Check ip and gateway of VMs via Contrail network

4.6 Check no connectivity between VMs in different tenants via Contrail network (a)

4.7 Check connectivity VMs with external network without floating IP via Contrail network (a)

4.8 Create a new network via Contrail WebUI

4.9 Check connectivity VMs with external network with floating IP via Contrail network (a)

4.10 Testing aggregation of network interfaces (bonding) (a)

4.11 Uninstall of plugin (a)

4.12 Uninstall of plugin with deployed environment (a)

4.13  Create and terminate networks and verify it in Contrail UI

4.14. Deploy cluster with 2 node groups

4.15 Verify traffic flow in jumbo-frames-enabled network (a)

4.16 Verify connectivity between vms with the same internal ips in different tenants (a)

4.17 Launch instance with new security group and check connection after deleting icmp and tcp rules (a)

-------------------
5. Failover testing
-------------------

5.1 Check Contrail HA using network problems (a)

5.2 Check Contrail HA using node problems (a)

5.3 Enable/disable port to VM (a)

5.4 Manual change network settings on instance (a)

5.5 Check ssh-connection by floating ip for vm after deleting floating ip

5.6 Check can not deploy Contrail cluster with  ‘contrail_db’ only (a)

5.7 Check can not deploy Contrail cluster with  ‘contrail_config’ only (a)

5.8 Check can not deploy Contrail cluster with  ‘contrail_control’ only (a)

5.9 Check can not deploy Contrail cluster with  ‘contrail_db’, ‘contrail_config’ only (a)

5.10 Check can not deploy Contrail cluster with  ‘contrail_db’, ‘contrail_control’ only (a)

5.11 Check can not deploy Contrail cluster with  ‘contrail_config’, ‘contrail_control’ only (a)

5.12 Check Contrail HA with deleting  ‘contrail_config’ (a)

5.13 Check Contrail HA with deleting  ‘contrail_control’ (a)

5.14 Check Contrail HA with deleting ‘contrail_db’, ‘contrail_config’ (a)

5.15 Check Contrail HA with deleting ‘contrail_db’, ‘contrail_control’ (a)

5.16 Check Contrail HA with deleting  ‘contrail_config’, ‘contrail_control’(a)

----------------------------------
Acceptance testing (exit criteria)
----------------------------------

90% of automation tests should be passed. Critical and high issues are fixed.
Such manual tests should be executed and passed (100% of them):

* Create and terminate networks and verify it in Contrail UI;
* Create a new network via Contrail WebUI;
* Deploy cluster with 2 node groups;
* Check ip and gateway of VMs via Contrail network;
* Check that Contrail UI settings fields are correct  in the Settings tab of the Fuel web UI;
* Check ssh-connection by floating ip for vm after deleting floating ip.

-------------
Test strategy
-------------

(a) those test cases will be automated for this release;
(bvt) those test cases will be using for build verification and run as unified bvt test;
if bvt is success all other automated tests will be used for maintenance after each iteration.

