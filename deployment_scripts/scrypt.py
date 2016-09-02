import yaml
from fuelclient.objects import Environment
env = Environment(1)
data = env.get_settings_data()
tor_configurations = data['editable']['contrail']['metadata']['versions'][0]['tor_agents_configurations']['value']
tor_configurations_yaml = yaml.load(tor_configurations)
