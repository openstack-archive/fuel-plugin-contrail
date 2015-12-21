New features in plugin version 3.0
==================================

*   Deployment is now role-based.
    Following roles are provided: Contrail-Control, Contrail-Config, Contrail-DB.
    This provides possibility to deploy these components on different servers.

*   VIPs for API and Web UI are now provided by Openstack Controllers and managed by Mirantis OpenStack HA.
    This provides possibility to place Contrail components in different L2/L3 segments.

*   Deployment tasks were rewritten to be more granular.

*   Plugin supports custom network templates feature of Fuel 7.0.
    Now it is possible to deploy a Contrail-enabled environment with reduced set of logical networks, e.g. Public, Management and Private nets can share the same interface.
    This simplifies routing configuration for large environments distributed across different L2 segments. More detailed information here :doc:`/using_network_templates`

