New features in plugin version 3.0.1
====================================

*   Deployment is now role-based.
    Following roles are provided: Contrail-Control, Contrail-Config, Contrail-DB.
    This provides a possibility to deploy these components on different servers.

*   VIPs for API and Web UI are now provided by Openstack Controllers and managed by Mirantis OpenStack HA.
    This provides a possibility to place Contrail components in different L2/L3 segments.

*   Deployment tasks were rewritten to be more granular.

*   DPDK-based vRouter. :doc:`/dpdk`

*   SR-IOV :doc:`/enable_sriov`

*   Plugin supports custom network templates feature of Fuel 7.0.
    Now it is possible to deploy a Contrail-enabled environment with reduced set of logical networks, e.g. Public, Management and Private nets can share the same interface.
    This simplifies routing configuration for large environments distributed across different L2 segments. More detailed information here :doc:`/using_network_templates`

*   HTTPS on public endpoints. If HTTPS is enabled in Fuel UI, the same certificate will be used for Contrail API and Contrail WebUI.

*   Contrail specific Ceilometer meters now supported.
