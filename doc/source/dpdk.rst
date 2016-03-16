DPDK
=====

Prerequisites
-------------

This guide assumes that you have `installed Fuel <https://docs.mirantis.com/openstack/fuel/fuel-7.0/user-guide.html>`_
and performed steps 5.3.1 - 5.3.9 from :doc:`/install_guide`.
To enable DPDK you need network card that supports DPDK. List of compatible adapters can be found on DPDK website - http://dpdk.org/doc/guides/nics/index.html 
Also it is important to remember, that only compute hosts can be configured with sriov role.

