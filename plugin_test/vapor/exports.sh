#!/usr/bin/env bash
# OpenStack credentials:
export OS_USERNAME=admin
export OS_PASSWORD=secret
export OS_TENANT_NAME=admin
export OS_AUTH_URL=http://127.0.0.1:5000/v3

# contrail endpoints
export CONTRAIL_API_URL=http://172.16.10.254:9100/
export CONTRAIL_ANALYTICS_URL=http://172.16.10.254:9081/

# os-faults config
export OS_FAULTS_CLOUD_DRIVER=tcpcloud
export OS_FAULTS_CLOUD_DRIVER_ADDRESS=192.168.10.100
export OS_FAULTS_CLOUD_DRIVER_KEYFILE=/home/jenkins/cloud.key
export OS_FAULTS_CLOUD_DRIVER_USERNAME=root

export CONTRAIL_ROLES_DISTRIBUTION_YAML=roles_distribution_example.yaml

#export OS_PROJECT_DOMAIN_NAME=default
#export OS_USER_DOMAIN_NAME=default
#export OS_PROJECT_NAME=admin
