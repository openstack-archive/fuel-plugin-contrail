#!/bin/sh

# Export specified settings
if [ -z $NODE_VOLUME_SIZE ]; then export NODE_VOLUME_SIZE=350; fi
if [ -z $OPENSTACK_RELEASE ]; then export OPENSTACK_RELEASE=Ubuntu; fi
if [ -z $BONDING ]; then export BONDING=true; fi
if [ -z $ENV_NAME ]; then export ENV_NAME="contrail"; fi
if [ -z $ADMIN_NODE_MEMORY ]; then export ADMIN_NODE_MEMORY=4096; fi
if [ -z $ADMIN_NODE_CPU ]; then export ADMIN_NODE_CPU=4; fi
if [ -z $SLAVE_NODE_MEMORY ]; then export SLAVE_NODE_MEMORY=4096; fi
if [ -z $SLAVE_NODE_CPU ]; then export SLAVE_NODE_CPU=4; fi

#Download actual fuel-qa
if [ -d fuel-qa ]; then rm -rf fuel-qa; fi
git clone -b stable/6.1 https://github.com/openstack/fuel-qa

echo
echo $*