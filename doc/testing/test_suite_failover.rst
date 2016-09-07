================
Failover testing
================


Check Contrail HA using network problems
----------------------------------------


ID
##

contrail_ha_with_network_problems


Description
###########

Check Contrail HA using network problems


Complexity
##########

advanced


Steps
#####

    1. Deploy openstack with HA (at lest 3 controllers and 3 nodes with contrail`s roles) and Ceph
    2. Run OSTF tests
    3. Run contrail health check tests
    4. Connect to a contrail controller host, stop the network interfaces connected to private and management networks
    5. Run OSTF tests
    6. Run contrail health check tests


Expected results
################

Ping should get a response for verifying HA


Check Contrail HA using node problems
-------------------------------------


ID
##

contrail_ha_with_node_problems


Description
###########

Check Contrail HA using node problems


Complexity
##########

advanced


Steps
#####

    1. Deploy openstack with HA (at lest 3 controllers
       and 3 nodes with contrail`s roles) and Ceph
    2. Run OSTF tests
    3. Run contrail health check tests
    4. Disable first contrail node via libvirt
    5. Run OSTF tests
    6. Run contrail health check tests
    7. Enable first contrail node and wait 6 minutes
    8. Disable second cotrail node
    9. Run OSTF test
    10. Run contrail health check tests
    11. Enable second contrail node and wait 6 minutes
    12. Disable third cotrail node
    13. Run OSTF tests
    14. Run contrail health check test
    15. Enable third node
    16. Run OSTF tests
    17. Run contrail health check test


Expected results
################

All steps must be completed successfully, without any errors.


Uninstall of plugin with environment
------------------------------------


ID
##

contrail_uninstall


Description
###########

Uninstall of plugin with environment


Complexity
##########

core


Steps
#####

    1. Install plugin and create cluster with activated plugin.
    2. Try to remove plugin and ensure that alert presents in cli:
       '400 Client Error: Bad Request (Can not delete plugin which
       is enabled for some environment.)'
    3. Remove environment.
    4. Remove plugin.
    5. Check that it was removed successfully.


Expected results
################

Alert is present when we try to remove plugin which is attached to enabled environment. When environment was removed, plugin is removed successfully too.


Cannot deploy dpdk with disable Nova Patch
------------------------------------------


ID
##

cannot_deploy_dpdk_without_nova_patch


Description
###########

Cannot deploy environment with dpdk, when "Nova Patch" was disabled


Complexity
##########

core


Steps
#####

    1. Log into the Fuel web UI
    2. Press "New OpenStack Environment"
    3. Specify Environment name as test
    4. Set QEMU or KVM as compute
    5. Select "Neutron with tunneling segmentation" as a network configuration
    6. Set "default" glance and cinder
    7. Do not use any additional services
    8. Press "Create"
    9. Open the Settings tab of the Fuel web UI
    10. Select the Contrail plugin checkbox and configure plugin settings
    11. Disable "Nova Patch" checkbox
    12. Configure network
    13. Add nodes with controller, compute+cinder, compute+dpdk and contrail-specified roles
    14. Start deploy



Expected results
################

Deploy must failed


Cannot deploy dpdk with disable Install Qemu and Libvirt from Contrail
----------------------------------------------------------------------


ID
##

cannot_deploy_dpdk_without_qemu_libvirt_contrail


Description
###########

Cannot deploy environment with dpdk, when "Install Qemu and Libvirt from Contrail" was disabled


Complexity
##########

advanced


Steps
#####

    1. Log into the Fuel web UI
    2. Press "New OpenStack Environment"
    3. Specify Environment name as test
    4. Set QEMU or KVM as compute
    5. Select "Neutron with tunneling segmentation" as a network configuration
    6. Set "default" glance and cinder
    7. Do not use any additional services
    8. Press "Create"
    9. Open the Settings tab of the Fuel web UI
    10. Select the Contrail plugin checkbox and configure plugin settings
    11. Disable "Install Qemu and Libvirt from Contrail" checkbox
    12. Configure network
    13. Add nodes with controller, compute+cinder, compute+dpdk and contrail-specified roles
    14. Start deploy


Expected results
################

Deploy must failed
