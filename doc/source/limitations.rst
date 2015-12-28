Limitations
===========

*   Contrail-specific statistics for Ceilometer were introduced in Contrail 2.2.
    This feature was not tested by Mirantis yet and not supported with plugin.

*   In some cases, Contrail Web UI can be unaccessible for some amount of time after removing or adding MOS Controller
    nodes to cluster.

*   Removing Contrail-DB nodes from cluster is not supported by plugin, it can lead to data loss, so this must be
    a manual procedure.
    Adding new Contrail-DB nodes to the environment is supported.

*   In case of using contrail service chaining with service instances, you may need to add *neutron* service user
    to a current tenant after you have deployed the environment:

    *   Open Horizon dashboard, navigate to Identity - Projects page.

    *   Click *modify users* button on the right side of *admin* project.

    *   Add *neutron* user to project members with *_member_* role.
