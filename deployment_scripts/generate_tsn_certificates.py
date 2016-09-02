#!/usr/bin/env python
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
#    This scipr is used to genereta all TSN certificates per claster
#
#    Example: $0 <env_id>
#    Example: ./generate_tsn_certificates.py 1
#
#    By pszypowicz@mirantis.com

import yaml
import sys, os
import logging
from fuelclient.objects import Environment
from subprocess import call

try:
    cluster_id = sys.argv[1]
except Exception:
    logging.warning('Provide cluster id as first parameter')
    sys.exit(1)

env = Environment(cluster_id)
data = env.get_settings_data()

try:
    tor_configurations = data['editable']['contrail']['metadata']['versions'][0]['tor_agents_configurations']['value']
except Exception:
    logging.warning('Cannot read tor agents configuration')
    sys.exit(2)

certificate_path = '/var/lib/fuel/certificates'

if not os.path.exists(certificate_path):
    os.makedirs(certificate_path)

directory = certificate_path + '/' + cluster_id + '/'

#generate certificates ca
call(['ovs-pki','init','--dir',directory])

if not os.path.exists(directory + 'certs/'):
    os.makedirs(directory + 'certs/')

tor_configurations_yaml = yaml.load(tor_configurations)
for i in tor_configurations_yaml:

    #tor_agent path
    tor_agent_directory = directory + 'certs/' + 'tor_agent_' + str(i)
    if not os.path.exists(tor_agent_directory):
        os.makedirs(tor_agent_directory)
        call(['ovs-pki','req+sign','tor_agent_' + str(i),'--dir',directory],cwd=tor_agent_directory)

    vtep_directory = directory + 'certs/' + 'vtep_' + str(i)
    if not os.path.exists(vtep_directory):
        os.makedirs(vtep_directory)
        call(['ovs-pki','req+sign','vtep_' + str(i),'--dir',directory],cwd=vtep_directory)

