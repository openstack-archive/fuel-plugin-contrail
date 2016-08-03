#!/bin/bash
#
#    Copyright 2016 Mirantis, Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
#
# This script provides the functions to upgrade the contrail packages and config files
# for existing Mirantis OpenStack environment deployed wth Fuel Contrail Plugin.
# It makes use of puppet manifests located in deployment_scripts/upgrade folder
# and contrail puppet module shipped within plugin.
#
# Upgrade steps
# 1. Upgrade contrail plugin to version 3.0.1+
# 2. Copy Contrail distribution packages to plugin folder on master node.
# 3. Run ./install.sh to populate the repositories with new packages.
# 4. Start the upgrade of control plane with ./upgrade.sh controllers.
# 5. After control plane has been upgraded, run ./upgrade.sh computes.
#
# Please note, that neutron operations will be unavailable during the process
# of contrail nodes upgrade (15-20 min window).
# The instances on compute nodes will lose network connectivity during the vrouter
# upgrade on particular compute node (upto 5 min).

# Functions
# Returns a list of nodes with role defined in argument, which are in 'ready' state,
# or a list of all ready nodes if no argument supplied
get_nodes_list () {
  local _role
  _role=$1
  if [ -z "$_role" ]; then
    _nodes=$(fuel node 2>/dev/null | grep 'ready' | cut -d "|" -f 1,7 | awk '{printf $1 ","}' | sed -e 's|,$||')
  elif [ "$_role" == "compute" ]; then
    _nodes=$(fuel node 2>/dev/null | grep 'ready' | cut -d "|" -f 1,7 | grep "$_role" | grep -v vmware | awk '{printf $1 ","}' | sed -e 's|,$||')
  else
    _nodes=$(fuel node 2>/dev/null | grep 'ready' | cut -d "|" -f 1,7 | grep "$_role" | awk '{printf $1 ","}' | sed -e 's|,$||')
  fi
  echo "$_nodes"
}

# Run the task on particular node
start_task_on_node () {
  local _nodes=$1
  local _tasks=$2

  fuel node --node-id "$_nodes" --task "$_tasks" 2>/dev/null
}

# Wait for task to complete or fail
wait_for_tasks () {
  local _timeout=60
  local _status
  while true ; do
    _status=$(fuel task 2>/dev/null | sort -n | tail -1 | cut -d "|" -f 2 | tr -d " ")
    case $_status in
      ready)
        break
      ;;
      error)
        exit 1
      ;;
      *)
        sleep $_timeout
      ;;
    esac
  done
}

# Steps
# Check the args, exit if none
[ $# -eq 0 ] && { echo "Usage: $0 <controllers|computes>"; exit 1; }

# Add the upgrade tasks to plugins deployment_tasks as skipped
grep -q "# Contrail upgrade tasks" deployment_tasks.yaml || cat upgrade_tasks.yaml >> deployment_tasks.yaml

# Sync the deployment tasks
fuel plugins --sync 2>/dev/null

# Rsync the plugins manifests
nodes=$(get_nodes_list)
start_task_on_node "$nodes" rsync_core_puppet
wait_for_tasks

# Run the upgrade tasks
case $1 in
controllers*)

    # Start the pre-upgrade tasks on contrail nodes
    nodes=$(get_nodes_list contrail)
    start_task_on_node "$nodes" upgrade-contrail-pre
    wait_for_tasks

    # Stop the contrail config services
    nodes=$(get_nodes_list contrail-config)
    start_task_on_node "$nodes" upgrade-contrail-stop-config
    wait_for_tasks

    # Stop the contrail collector services
    nodes=$(get_nodes_list contrail-analytics)
    if [ -n "$nodes" ]; then
      start_task_on_node "$nodes" upgrade-contrail-stop-analytics
    else
      nodes_cfg=$(get_nodes_list contrail-config)
      start_task_on_node "$nodes_cfg" upgrade-contrail-stop-analytics
    fi
    wait_for_tasks

    # Start the upgrade tasks on database nodes
    nodes=$(get_nodes_list contrail-db)
    start_task_on_node "$nodes" upgrade-contrail-db
    wait_for_tasks

    # Start the upgrade tasks on config nodes
    nodes=$(get_nodes_list contrail-config)
    start_task_on_node "$nodes" upgrade-contrail-config
    wait_for_tasks

    # Start the upgrade tasks on collector nodes
    nodes=$(get_nodes_list contrail-analytics)
    if [ -n "$nodes" ]; then
      start_task_on_node "$nodes" upgrade-contrail-analytics
    else
      nodes_cfg=$(get_nodes_list contrail-config)
      start_task_on_node "$nodes_cfg" upgrade-contrail-analytics
    fi
    wait_for_tasks

    # Start the upgrade tasks on control nodes, one by one
    nodes=$(get_nodes_list contrail-control)
    for node in ${nodes//,/ }
    do
      start_task_on_node "$node" upgrade-contrail-control
      wait_for_tasks
    done

    # Start the post-upgrade tasks on contrail nodes
    nodes=$(get_nodes_list contrail)
    start_task_on_node "$nodes" upgrade-contrail-post
    wait_for_tasks

    # Start the upgrade tasks on config nodes
    nodes=$(get_nodes_list controller)
    start_task_on_node "$nodes" upgrade-contrail-controller
    wait_for_tasks
;;

computes*)

    # Start the repo tasks on compute nodes
    nodes=$(get_nodes_list compute)
    start_task_on_node "$nodes" contrail-repository
    wait_for_tasks

    # Start the upgrade tasks on compute nodes, one by one
    nodes=$(get_nodes_list compute)
    for node in ${nodes//,/ }
    do
      start_task_on_node "$node" upgrade-contrail-compute
      wait_for_tasks
    done
    ;;
*)
    echo "Incorrect args specified"; exit 1
    ;;
esac
