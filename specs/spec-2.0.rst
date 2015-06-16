==============================
Fuel Contrail plugin 2.0 specs
==============================


Get rid of fabric scripts
=========================

Problem description
-------------------

Contrail plugin 1.0 uses fabric scripts shipped by Juniper within their Contrail packages.
We should get rid of fabric scripts and implement puppet-driven installation.

Reasons
-------
 * Fabric makes installation process complex and hard to debug.
 * Fabric scripts behaviour is not idempotent. It’s quite important for normal Fuel operation. We use some dirty hacks to accomplish it for now.
 * Puppet is a native way to install and configure things in Fuel.
 * Fabric scripts make impossible by design to use plugin with Opencontrail

Proposed solution
------------------

Eliminate “contrail::run_fabric” class and all its invocations in favor of puppet manifests.

Such as:
    run_fabric { 'prov_control_bgp'}
    run_fabric { 'prov_external_bgp'}
    run_fabric { 'prov_metadata_services'}
    run_fabric { 'prov_encap_type'}
    run_fabric { 'install_database'}
    run_fabric { 'setup_database'}
    run_fabric { 'install_cfgm'}
    run_fabric { 'install_control'}
    run_fabric { 'install_collector'}
    run_fabric { 'install_webui'}
    run_fabric { 'setup_contrail_keepalived'}
    run_fabric { 'fixup_restart_haproxy_in_collector'}
    run_fabric { 'fix-service-tenant-name'}
    run_fabric { 'setup_cfgm'}
    run_fabric { 'setup_control'}
    run_fabric { 'setup_collector'}
    run_fabric { 'setup_webui'}

Provide better support for multiple L2 segments in plugin-enabled environments
==============================================================================

Problem description
-------------------

The Fuel Contrail Plugin version 1.0 uses Neutron with VLAN segmentation as the only network type supported.
This network type does not fully support Node groups feature introduced in Fuel 6.0 to simplify the deployments in multi-rack environments with different L2 network in each rack.

Proposed solution
-----------------

Updated the plugin to support GRE segmentation and use Private network settings from Fuel.

Use “plugin role” feature from Fuel 7.0
=======================================

Problem description
-------------------

Plugin installation process is complex and not obvious for end users because of workaround with base-os role and mandatory node_user_name for every node with plugin functions.

Proposed solution
-----------------

Rewrite plugin logic to drop the workaround and utilize new plugin SDK feature Plugin role to enable selection of plugin-defined node roles for end-user.

Related blueprints
------------------
https://blueprints.launchpad.net/fuel/+spec/role-as-a-plugin

Use Neutron supported by Mirantis
=================================

Problem description
-------------------

Contrail-enabled compute nodes are using juniper-shipped Neutron which is not supported by Mirantis. Updates and security fixes should be applied manually.

Proposed solution
-----------------

Use Mirantis OpenStack Neutron running on OpenStack controllers instead of shipped by Juniper one.
