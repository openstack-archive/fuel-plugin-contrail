Introduction
============

This document contains instructions for installing and configuring Contrail plugin for Fuel.

Key terms, acronyms and abbreviations
-------------------------------------

+--------------------+-------------------------------------------------------------------+
| Juniper Contrail   | Contrail Cloud Platform is a foundational element of Juniper's    |
|                    | open cloud networking and NFV solutions.                          |
+--------------------+-------------------------------------------------------------------+
| SDN                | Software defined network                                          |
+--------------------+-------------------------------------------------------------------+
| RESTful API        | Representational state transfer application programming interface |
+--------------------+-------------------------------------------------------------------+
| IDS                | Intrusion detection system                                        |
+--------------------+-------------------------------------------------------------------+
| DPI                | Deep packet inspection                                            |
+--------------------+-------------------------------------------------------------------+
| VIP                | virtual IP address                                                |
+--------------------+-------------------------------------------------------------------+
| BGP                | Border gateway protocol                                           |
+--------------------+-------------------------------------------------------------------+
| AS                 | Autonomous system                                                 |
+--------------------+-------------------------------------------------------------------+
| Contrail vRouter   | Contrail vRouter is part of the compute node, which gets          |
|                    | reachability information from the control plane and ensures native|
|                    | L3 services for host-based virtual machines.                      |
+--------------------+-------------------------------------------------------------------+
| MOS                | Mirantis OpenStack                                                |
+--------------------+-------------------------------------------------------------------+

Overview
--------

Contrail plugin for Fuel provides the functionality to add Contrail SDN for Mirantis OpenStack as networking backend option
using Fuel Web UI in a user-friendly manner.
Juniper Networks Contrail is an open software defined networking solution that automates and orchestrates the creation of
highly scalable virtual networks.

Contrail features:

*   Powerful API calls (REST or direct python class calls)

*   Analytics engine: Traffic flow reports, statistics

*   Network management at 2-4 OSI layers

*   Service chaining architecture: you can transparently pass traffic through service instances, such as IDS, firewalls, DPI.

*   Fine grained virtual network access policy control

