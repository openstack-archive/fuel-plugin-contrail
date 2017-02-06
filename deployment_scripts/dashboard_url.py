__author__ = 'Illia Polliul'

from argparse import ArgumentParser
import requests
from fuelclient.client import APIClient
from fuelclient.objects.environment import Environment

def parseargs():
    parser = ArgumentParser(
    	usage="""
    	dashboard_url --env 1 --vip public --port 8143 --name Contrail \
    	--description 'Dashboard for Contrail Web UI'
    	""")
    parser.add_argument('-e', '--env', default = '1', help = 'Environment')
    parser.add_argument('-v', '--vip_name', default = 'public', help = 'VIP name')
    parser.add_argument('-p', '--port', default = '8143', help = 'Port number')
    parser.add_argument('-t', '--title', default = 'Contrail', help = 'Link title')
    parser.add_argument('-d', '--description', default = '', help = 'Link description')

    return vars(parser.parse_args())


token = APIClient.auth_token
api_url = 'http://127.0.0.1:8000/api/clusters/' + env + '/plugin_links'
headers = {'X-Auth-Token': token}

links = requests.get(api_url, headers = headers).json()
plugin_url = (item for item in links if item['title'] == name ).next()['url']

vips = Environment(env).get_vips_data()
vip = (item for item in vips if item['vip_name'] == vip_name ).next()['ip_addr']

url = 'https://' + vip + ':8143/'

plugin_link_data = {
	'title': title,
	'description': description,
	'url': url,
}

if !contrail_url :
	requests.post( contrail_link_data, )

if contrail_url != url :
	requests.put( contrail_link_data, )

if __name__ == '__main__':
	params = parseargs()
	jira = connect_to_jira()
	print_dba_tickets()