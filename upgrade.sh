#!/bin/sh
# This script provides the functions to upgrade the contrail packages on existing env
# It makes use of puppet manifests located in deployment_scripts/upgrade folder
# and contrail puppet module

# Functions
# Returns a list of nodes with role defined in argument, which are in 'ready' state,
# or a list of all ready nodes if no argument supplied
get_nodes_list () {
	local _role=$1
    if [ -z "$_role" ]; then
    	local _nodes=$(fuel node | grep 'ready' 2>/dev/null | cut -d "|" -f 1,7 | awk '{printf $1 ","}' | sed -e 's|,$||')
    elif [ $_role eq "compute" ]; then
    	local _nodes=$(fuel node | grep 'ready' 2>/dev/null | cut -d "|" -f 1,7 | grep $_role | grep -v vmware | awk '{printf $1 ","}' | sed -e 's|,$||')
    else
    	local _nodes=$(fuel node | grep 'ready' 2>/dev/null | cut -d "|" -f 1,7 | grep $_role | awk '{printf $1 ","}' | sed -e 's|,$||')
    fi
    echo $_nodes
}

# Run the task on particular node 
start_task_on_node () {
	local _nodes=$1
	local _tasks=$2
	fuel node --node-id $_nodes --task $_tasks
}

# Wait for task to complete or fail
wait_for_tasks () {
  local _timeout=60
  local _status
  while true ; do
    _status=$(fuel task | sort -n | tail -1 | cut -d "|" -f 2 | tr -d " ")
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
# Add the upgrade tasks to plugins deployment_tasks as skipped
grep -q "# Contrail upgrade tasks" deployment_tasks.yaml || cat upgrade_tasks.yaml >> deployment_tasks.yaml

# Sync the deployment tasks
fuel plugins --sync

# Rsync the plugins manifests
nodes=$(get_nodes_list)
start_task_on_node $nodes rsync_core_puppet
wait_for_tasks

# Start the pre-upgrade tasks on contrail nodes
nodes=$(get_nodes_list contrail)
start_task_on_node $nodes upgrade-contrail-pre
wait_for_tasks

# Stop the contrail collector and config services
nodes=$(get_nodes_list contrail-config)
start_task_on_node $nodes upgrade-contrail-stop
wait_for_tasks

# Start the upgrade tasks on database nodes
nodes=$(get_nodes_list contrail-db)
start_task_on_node $nodes upgrade-contrail-db
wait_for_tasks

# Start the upgrade tasks on config nodes
nodes=$(get_nodes_list contrail-config)
start_task_on_node $nodes upgrade-contrail-config
wait_for_tasks

# Start the upgrade tasks on control nodes, one by one
nodes=$(get_nodes_list contrail-control)
for node in $nodes do
	start_task_on_node $node upgrade-contrail-control
	wait_for_tasks
done

# Start the post-upgrade tasks on contrail nodes
nodes=$(get_nodes_list contrail)
start_task_on_node $nodes upgrade-contrail-post
wait_for_tasks

# Start the upgrade tasks on config nodes
nodes=$(get_nodes_list controller)
start_task_on_node $nodes upgrade-contrail-controller
wait_for_tasks

# Start the repo tasks on compute nodes
nodes=$(get_nodes_list compute)
start_task_on_node $nodes contrail-repository
wait_for_tasks

# Start the upgrade tasks on compute nodes, one by one
nodes=$(get_nodes_list compute)
for node in $nodes do
	start_task_on_node $node upgrade-contrail-compute
	wait_for_tasks
done
