# General configuration
$settings = hiera('contrail')
$network_scheme = hiera("network_scheme")
$uid = hiera("uid")

# Network configuration
prepare_network_config($network_scheme)
$ifname = get_network_role_property('private','interface')
$range_first = $settings['contrail_private_start']
$range_last = $settings['contrail_private_end']
$cidr = $settings['contrail_private_cidr']
$node_ip=get_ip_from_range($range_first,$range_last,$cidr,$uid)
$node_role = hiera('role')

# Package configuration
$master_ip = hiera('master_ip')
$master_port = '8080'
$plugin_version = $settings['metadata']['plugin_version']

class { contrail::packages:
  plugin_version => $plugin_version,
  master_ip      => $master_ip,
  master_port    => $master_port,
  install        => ['python-crypto','python-netaddr','python-paramiko',
                    'contrail-fabric-utils','contrail-setup'],
  pip_install    => ['ecdsa-0.10','Fabric-1.7.0'],
  responsefile   => 'contrail.preseed',
}

class { 'contrail::network':
  node_role   => 'base-os',
  node_ip     => $node_ip,
  ifname      => $ifname,
  cidr        => $cidr,
}

class { contrail::ssh:
  password_auth => 'yes',
}

class { 'contrail::network':
  node_role => 'compute',
  range_first => $range_first,
  range_last => $range_last,
  cidr => $cidr,
  uid => $uid,
}
