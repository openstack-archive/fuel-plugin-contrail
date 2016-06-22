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
| TOR                | Top of rack                                                       |
+--------------------+-------------------------------------------------------------------+
| TSN                | TOR Services Node                                                 |
+--------------------+-------------------------------------------------------------------+

Overview
--------

Contrail plugin for Fuel adds Contrail SDN to Mirantis OpenStack as a networking back end option
using Fuel web UI in a user-friendly manner.
Juniper Networks Contrail is an open software defined networking solution that automates and
orchestrates the creation of highly scalable virtual networks.

Contrail features:

*   Powerful API calls (REST or direct python class calls)

*   Analytics engine: traffic flow reports, statistics

*   Network management at 2-4 OSI layers

*   Service chaining architecture: you can transparently pass traffic through service instances
    such as IDS, firewalls, and DPI.

*   Fine grained virtual network access policy control
