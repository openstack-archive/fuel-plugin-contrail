Limitations
===========

*   Plugin does not support removing Contrail-Controller and Analytics-DB nodes from a cluster.
    This can lead to data loss and must be a manual procedure.
    Plugin supports adding new Contrail-DB nodes to the environment.

*   The Fuel Networking option "Assign public network to all nodes" is not compatible with Contrail Plugin.

*   In case of using contrail service chaining with service instances, you may need to add *neutron* service user
    to a current project after you have deployed the environment:

    *   Open OpenStack Dashboard, navigate to the :guilabel:`Identity - Projects` page.

    *   Click :guilabel:`modify users` button on the right side of the ``admin`` project.

    *   Add the ``neutron`` user to project members with ``_member_`` role.

*   Changing the default OpenStack project name is not supported. Default project name should be ``admin``.

*   The password of OpenStack ``admin`` user should not contain following characters: ``$``, `````, ``\\`` and ``!``

*   Upgrade procedure based on custom deployment graphs does not support upgrading nodes with roles dpdk, tsn and vmware.
    Contrail packages upgrades should be done manually on these nodes.
