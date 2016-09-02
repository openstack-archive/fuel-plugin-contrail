import yaml
import sys, os
from fuelclient.objects import Environment
from subprocess import call

try:
    cluster_id = sys.argv[1]
except:
    print "Provide cluster id as first parameter"
    sys.exit(1)

env = Environment(cluster_id)
data = env.get_settings_data()

try:
    tor_configurations = data['editable']['contrail']['metadata']['versions'][0]['tor_agents_configurations']['value']
except:
    print "Cannot read tor agents configuration"
    sys.exit(2)

if not os.path.exists('/var/lib/fuel/certificates'):
    os.makedirs('/var/lib/fuel/certificates')

directory = '/var/lib/fuel/certificates/' + cluster_id + '/'

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

