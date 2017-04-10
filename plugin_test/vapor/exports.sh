#!/bin/bash
export OS_USERNAME=admin
export OS_PASSWORD=password
export OS_TENANR_NAME=admin
export OS_AUTH_URL=http://10.167.4.10:35357/v3
export VIRTUAL_DISPLAY=1

export OS_FAULTS_CLOUD_DRIVER=tcpcloud
export OS_FAULTS_CLOUD_DRIVER_KEYFILE=/opt/vapor/cloud.key
export OS_FAULTS_CLOUD_DRIVER_ADDRESS=172.16.49.66
export OS_FAULTS_CLOUD_DRIVER_USERNAME=root

export CONTRAIL_ROLES_DISTRIBUTION_YAML=roles_mcp10_contrail.yaml
export CONTRAIL_API_URL=http://10.167.4.20:9100/
export CONTRAIL_ANALYTICS_URL=http://10.167.4.30:8081/

#export DEFAULT_FLAVOR_RAM="2048"
#export DEFAULT_FLAVOR_CPU="2"
#export DEFAULT_FLAVOR_DISK="20"
#export DEFAULT_FLAVOR_METADATA='{"hw:mem_page_size":"large"}'
