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

    1. Login as admin to Openstack Horizon UI
    2. Launch 2 new instances
    3. Connect to the first instance via VNC (Horizon) and send ping to the second instance
    4. Connect to a contrail controller host, stop the network interfaces connected to private and management networks.


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

    1. Login as admin to Openstack Horizon UI
    2. Launch 2 new instances
    3. Connect to the first instance via VNC (Horizon) and ping the second instance
    4. With a pause of 5-10 minutes turn off and turn on each of Contrail Nodes


Expected results
################

Ping should get a response.


Uninstall of plugin with deployed environment
---------------------------------------------


ID
##

uninstall_contrail_plugin_with_deployed_environment


Description
###########

Uninstall of plugin with deployed environment


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
