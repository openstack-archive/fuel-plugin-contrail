#!/bin/bash
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


# This script installs contrail packages to the proper paths and generates repo metadata.

# REQUIREMENTS:
#   - Paths to Juniper Contrail packages (could be retrieved from Juniper) for Centos/Ubuntu must be set at UBUNTU_PKG and CENTOS_PKG variables.
#   - Plugin path must be correctly set

# USAGE:
#   - Just ./install.sh


set -ex

PLUGIN_PATH="/var/www/nailgun/plugins/contrail-5.1"
#Now uses the latest package file
UBUNTU_PKG=$(find $PLUGIN_PATH -maxdepth 1 -name 'contrail-install-packages*.deb' -exec stat -c "%y %n" {} + | sort -r | head -n 1 | cut -d' ' -f 4)
CENTOS_PKG=$(find $PLUGIN_PATH -maxdepth 1 -name 'contrail-install-packages*.rpm' -exec stat -c "%y %n" {} + | sort -r | head -n 1 | cut -d' ' -f 4)
VMWARE_PKG=$(find $PLUGIN_PATH -maxdepth 1 -name 'contrail-install-vcenter-plugin*.deb' -exec stat -c "%y %n" {} + | sort -r | head -n 1 | cut -d' ' -f 4)

yum -y install dpkg dpkg-dev createrepo

if [ ! -f "$UBUNTU_PKG" ] && [ ! -f "$CENTOS_PKG" ];
then
  echo "No Juniper Contrail packages found at $PLUGIN_PATH. Updating existing plugin repos."
  cd $PLUGIN_PATH/repositories/ubuntu/
  dpkg-scanpackages ./ | gzip -c - > Packages.gz
  cd $PLUGIN_PATH/repositories/centos/
  createrepo .
fi

if [ -f "$UBUNTU_PKG" ];
then
  DEB=$(mktemp -d)
  dpkg -x "$UBUNTU_PKG" "$DEB"
  cd $PLUGIN_PATH/repositories/ubuntu/
  find . -type f -name "*.deb" -delete
  tar -xzvf "$DEB"/opt/contrail/contrail_packages/contrail_debs.tgz -C "$PLUGIN_PATH"/repositories/ubuntu/
  if [ -f "$VMWARE_PKG" ];
  then
    cp "$VMWARE_PKG" "$PLUGIN_PATH"/repositories/ubuntu/
    DEB2=$(mktemp -d)
    dpkg -x "$VMWARE_PKG" "$DEB2"
    cp "$DEB2"/opt/contrail/contrail_vcenter_plugin_install_repo/*.deb "$PLUGIN_PATH"/repositories/ubuntu/
  fi
  DPDK_PKG=$(find $PLUGIN_PATH -maxdepth 4 -name 'dpdk-depends-packages*.deb' -exec stat -c "%y %n" {} + | sort -r | head -n 1 | cut -d' ' -f 4)
  if [ -f "$DPDK_PKG" ];
  then
    DEB3=$(mktemp -d)
    cp "$DPDK_PKG" "$DEB3"
    cd "$DEB3" && ar vx dpdk-depends-packages*.deb && tar xf data.tar.xz && cp "$DEB3"/opt/contrail/contrail_install_repo_dpdk/contrail-dpdk-kernel-modules-dkms*.deb "$PLUGIN_PATH"/repositories/ubuntu/
  fi
  cd "$PLUGIN_PATH"/repositories/ubuntu/
  dpkg-scanpackages ./ | gzip -c - > Packages.gz
fi

if [ -f "$CENTOS_PKG" ];
then
  RPM=$(mktemp -d)
  cd "$RPM"
  rpm2cpio "$CENTOS_PKG" | cpio -id
  mkdir -p "$PLUGIN_PATH"/repositories/centos/Packages
  cd "$PLUGIN_PATH"/repositories/centos/
  find Packages -type f -name "*.rpm" -delete
  tar -xzvf "$RPM"/opt/contrail/contrail_packages/contrail_rpms.tgz -C "$PLUGIN_PATH"/repositories/centos/Packages/
  createrepo .
fi

echo "DONE"
