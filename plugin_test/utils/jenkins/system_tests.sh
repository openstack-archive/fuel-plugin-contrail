#!/bin/bash

if [ !	 -d plugin_test ]; then echo "Please start this script inside plugin directory"; exit 1; fi

# Export specified settings
if [ -z $LOGS_DIR ]; then export LOGS_DIR=`pwd`/logs; fi
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

ln -s `pwd`/plugin_test `pwd`/fuel-qa/fuelweb_test/
WORKSPASE=`pwd`/fuel-qa
sed -i '/plugin_contrail/d' fuel-qa/fuelweb_test/run_tests.py
Line=$(grep -n 'test_zabbix' fuel-qa/fuelweb_test/run_tests.py | awk -F ':' '{print $1} ')
sed -i "${Line}r fuel-qa/fuelweb_test/plugin_test/import.txt" fuel-qa/fuelweb_test/run_tests.py



if [ -z $1 ]; then exit 0 ; fi

sh -x "fuel-qa/utils/jenkins/system_tests.sh" -w $WORKSPASE $* &

  SYSTEST_PID=$!
  echo waiting for system tests to finish
  wait $SYSTEST_PID
  export RES=$?
  echo ENVIRONMENT NAME is $ENV_NAME
  #dos.py net-list $ENV_NAME
  virsh net-dumpxml ${ENV_NAME}_admin | grep -P "(\d+\.){3}" -o | awk '{print "Fuel master node IP: "$0"2"}'

  echo Result is $RES

#workaround for jenkins marking tests as failed on segfaults
  if [ $RES -eq 139 ]
  then
    grep 'errors="0"' nosetests.xml | grep -q 'failures="0"' && echo SEGFAULT workaround && RES=0
  fi 

