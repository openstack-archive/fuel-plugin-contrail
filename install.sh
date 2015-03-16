#!/bin/bash

# This script installs contrail packages to the proper paths and generates repo metadata.

# REQUIREMENTS:
#   - Paths to Juniper Contrail packages (could be retrieved from Juniper) for Centos/Ubuntu must be set at UBUNTU_PKG and CENTOS_PKG variables.
#   - Plugin path must be correctly set

# USAGE:
#   - Just ./install.sh


set -ex

PLUGIN_PATH="/var/www/nailgun/plugins/contrail-1.0.0"
UBUNTU_PKG=`find $PLUGIN_PATH -maxdepth 1 -name 'contrail-install-packages*.deb'`
CENTOS_PKG=`find $PLUGIN_PATH -maxdepth 1 -name 'contrail-install-packages*.rpm'`

yum -y install dpkg-devel createrepo

if [ ! -f "$UBUNTU_PKG" ] && [ ! -f "$CENTOS_PKG" ];
  then
    echo "ERROR: No packages found at  $PLUGIN_PATH" 
    exit 1
  fi

if [ -f "$UBUNTU_PKG" ];
  then
    DEB=`mktemp -d`
    dpkg -x $UBUNTU_PKG $DEB
    tar -xzvf $DEB/opt/contrail/contrail_packages/contrail_debs.tgz -C $PLUGIN_PATH/repositories/ubuntu/
    cd $PLUGIN_PATH/repositories/ubuntu/
    dpkg-scanpackages ./ | gzip -c - > Packages.gz
  fi

if [ -f "$CENTOS_PKG" ];
  then
    RPM=`mktemp -d`
    cd $RPM
    rpm2cpio $CENTOS_PKG | cpio -id
    tar -xzvf $RPM/opt/contrail/contrail_packages/contrail_rpms.tgz -C $PLUGIN_PATH/repositories/centos/
    cd $PLUGIN_PATH/repositories/centos/
    createrepo .
  fi

echo "DONE"





