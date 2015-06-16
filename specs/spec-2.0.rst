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

Update the plugin to support Neutron with GRE segmentation Fuel network type and use Private network settings set in Fuel Web UI.

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

Contrail-enabled OpenStack environment is using juniper-shipped Neutron which is not supported by Mirantis. Updates and security fixes for Neutron component should be applied manually.

Proposed solution
-----------------

Use Mirantis OpenStack Neutron running on OpenStack controllers instead of shipped by Juniper one.
Automate installation of contrail neutron plugin on controllers.

Implementation
==============

Assignee(s)
-----------

Primary assignee:

- Oleksandr Martsyniuk <omartsyniuk@mirantis.com> - feature lead, developer

Other contributors:

- Vyacheslav Struk <vstruk@mirantis.com> - developer

Project manager:

- Andrian Noga <anoga@mirantis.com>

Quality assurance:

- Oleksandr Kosse <okosse@mirantis.com> - qa
- Iryna Vovk <ivovk@mirantis.com> - qa

Docs Lead:

- Irina Povolotskaya <ipovolotskaya@mirantis.com> - technical writer

Work Items
----------

* Create pre-dev environment and manually deploy Contrail software
* Create Fuel plugin bundle, which contains deployments scripts, puppet modules and metadata
* Entend the puppet module with the following functions:

 - full puppet-based Contrail controllers deployment and configuration
 - support for Neutron with GRE segmentation network type in Fuel
 - contrail neutron plugin installation
 - support for plugin-based node role

* Test Contrail plugin version 2.0
* Update Documentation

