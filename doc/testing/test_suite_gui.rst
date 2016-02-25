===========
GUI testing
===========


Install Plugin
--------------


ID
##

install_contrail


Description
###########

Install Contrail Plugin and create cluster


Complexity
##########

Smoke


Steps
#####

    1. Upload a plugin to Fuel Master node using scp.
    2. Connect to Fuel Master node via ssh.
    3. Install plugin with fuel-cli.
    4. Connect to Fuel web UI.
    5. Click on the 'Create Environment' button.
    6. Configure Environment with the 'Neutron with tunneling segmentation' network configuration.
    7. Click on 'Settings'
    8. Verify that Contrail Plugin Configure Checkboxes are present and active.


Expected results
################

Contrail Plugin Configure Checkboxes are available


Check that Contrail UI settings fields are correct in the Settings tab of the Fuel web UI
-----------------------------------------------------------------------------------------


ID
##

correctness_contrail_fields


Description
###########

Check that Contrail UI settings fields are correct  in the Settings tab of the Fuel web UI


Complexity
##########

advanced


Steps
#####

    1. Log into the Fuel web UI
    2. Create 'New OpenStack Environment'
    3. Specify Environment name as test
    4. Set QEMU or KVM as compute
    5. Select 'Neutron with tunneling segmentation' as a network configuration
    6. Set 'default' glance and cinder
    7. Do not use any Additional Services
    8. Press 'Create'
    9. Open the Settings tab of the Fuel web UI
    10. Select the Contrail plugin checkbox
    11. Verify validation of the field 'AS number' with: set as empty, set  literal value, set 0 or 65536, other settings leave as default
    12. Verify validation 'GW IP' field with: verify that  this field may be empty if gateway is not used, set invalid ip address ('256.256.256.256'), other settings leave as default


Expected results
################

Appropriate error message should appear in 11 and 12 steps


Verify HTTPS on Contrail with selected TLS for OPenStack public endpoints
-------------------------------------------------------------------------


ID
##

https_TLS_selected


Description
###########

Verify HTTPS on Contrail with selected TLS for OPenStack public endpoints


Complexity
##########

advanced


Steps
#####

    1. Deploy Contrail cluster with selected TLS for OPenStack public endpoints
    2. Login as admin to Openstack Horizon UI
    3. Get fingerprints from certificate viewer
    4. Login as admin to Contrail UI
    5. Get fingerprints
    6. Verify that keys from Horizon and Contrail UIs are identical


Expected results
################

All steps must be completed successfully, without any errors.


Verify HTTPS on Contrail with deselected TLS for OPenStack public endpoints
---------------------------------------------------------------------------


ID
##

https_TLS_deselected


Description
###########

Verify HTTPS on Contrail with deselected TLS for OPenStack public endpoints


Complexity
##########

advanced


Steps
#####

    1. Deploy Contrail cluster with deselected TLS for OPenStack public endpoints
    2. Login as admin to Openstack Horizon UI
    3. Get fingerprints from certificate viewer
    4. Login as admin to Contrail UI
    5. Get fingerprints
    6. Verify that keys from Horizon and Contrail UIs are different


Expected results
################

All steps must be completed successfully, without any errors.
