#!/bin/bash

# This script installs contrail packages to the proper paths and generates repo metadata.

# REQUIREMENTS:
#   - Paths to Juniper Contrail packages (could be retrieved from Juniper) for Centos/Ubuntu must be set at UBUNTU_PKG and CENTOS_PKG variables.
#   - Plugin path must be correctly set

# USAGE:
#   - Just ./install.sh


set -ex

PLUGIN_PATH="/var/www/nailgun/plugins/contrail-1.0.0"
UBUNTU_PKG="$PLUGIN_PATH/contrail-install-packages_2.01-41~icehouse_all.deb"
CENTOS_PKG="$PLUGIN_PATH/contrail-install-packages-2.01-41~icehouse.el6.noarch.rpm"

yum -y install dpkg-devel createrepo
DEB=`mktemp -d`
RPM=`mktemp -d`

dpkg -x $UBUNTU_PKG $DEB
tar -xzvf $DEB/opt/contrail/contrail_packages/contrail_debs.tgz -C $PLUGIN_PATH/repositories/ubuntu/
cd $PLUGIN_PATH/repositories/ubuntu/
dpkg-scanpackages ./ | gzip -c - > Packages.gz

cd $RPM
rpm2cpio $CENTOS_PKG | cpio -id
tar -xzvf $RPM/opt/contrail/contrail_packages/contrail_rpms.tgz -C $PLUGIN_PATH/repositories/centos/
cd $PLUGIN_PATH/repositories/centos/
createrepo .

echo "DONE"





