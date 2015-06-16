==============================
Fuel contrail plugin 2.0 specs
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
 * Fab’s make impossible by design to use plugin with Opencontrail

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


Use “plugin role” feature from fuel 7.0
=======================================

Problem description 
-------------------

Plugin installation process is complex and not obvious for end users because of workaround with base-os role and mandatory node_user_name for every node with plugin functions.

Proposed solution
-----------------

Rewrite plugin logic to drop the workaround and utilize new plugin SDK feature Plugin role to enable selection of plugin-defined node roles for end-user.

Use neutron supported by Mirantis
=================================

Problem description
-------------------

Contrail-enabled compute nodes are using juniper-shipped neutron which is not supported by fuel team. Updates and security fixes should be applied manually.

Proposed solution
-----------------

Use fuel’s neutron instead of shipped by juniper one. JUNIPER-SHIPPED NEUTRON IS NOT SUPPORTED BY MIRANTIS (security updates etc)

ESXI Hypervisor support for contrail
====================================

Problem description
-------------------

While the version 1.0 of plugin deploys Contrail and MOS with KVM support, Fuel-driven deployments also can make use of VMWare vCenter as hypervisor. It will be great if the plugin-based deployment will support both hypervisors.

Proposed solution
-----------------

Implement support for VMWare ESXI Hypervisor in contrail-enabled environments.







