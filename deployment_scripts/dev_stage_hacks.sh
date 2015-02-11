#!/bin/bash

# FOR DEVELOPMENT STAGE ONLY

# Overrides old l23network with a newer version.
# This script  must be executed as pre-deploymeny tasks, or plugin deploy WILL fail.
# Again, this hacks are for development stage ONLY, until new https://review.openstack.org/154032 is not merged to master


# All the patches and modules are tested and compatible with #98 build of fuel 6.1

# Moved to tasks.yaml
#python ./hacks/yamlhack.py /etc/compute.yaml ./hacks/compute_schema.yaml
patch /etc/puppet/modules/osnailyfacter/modular/netconfig.pp ./hacks/osnailyfacter_netconfig.patch
rm -rf /etc/puppet/modules/l23network

tar -C ./hacks/ -xzf ./hacks/filemapper.tar.gz
tar -C ./hacks/ -xzf ./hacks/l23network.tar.gz
cp -r ./hacks/l23network /etc/puppet/modules/
cp -r ./hacks/filemapper /etc/puppet/modules/

# Must be used until https://review.openstack.org/155763/ is merged to master
patch /etc/puppet/modules/osnailyfacter/modular/hiera.pp ./hacks/hiera_order.patch


