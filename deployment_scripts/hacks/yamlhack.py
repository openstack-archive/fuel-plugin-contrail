#!/usr/bin/python

import yaml
import sys

if len(sys.argv) != 3:
    print """
Temporary workaround.
Overwrites "network_scheme" section with new content.
Usage ./yamlhack.py <role.yaml> <replacement_scheme.yaml>
"""
    sys.exit(1)

stream_orig = file(sys.argv[1], 'r')
stream_new = file(sys.argv[2], 'r')

orig = yaml.load(stream_orig)
stream_orig.close()
new_scheme = yaml.load(stream_new)

orig['network_scheme'] = new_scheme['network_scheme']

stream_out = file(sys.argv[1], 'w')
yaml.dump(orig, stream_out, default_flow_style=False)

