include contrail

class { 'contrail::network':
  node_role   => 'base-os',
  node_ip     => $contrail::node_ip,
  ifname      => $contrail::ifname,
  cidr        => $contrail::cidr,
} ->

class { contrail::ssh:
  password_auth => 'yes',
} ->

class { contrail::packages:
  plugin_version => $contrail::plugin_version,
  master_ip      => $contrail::master_ip,
  master_port    => $contrail::master_port,
  install        => ['python-crypto','python-netaddr','python-paramiko',
                    'contrail-fabric-utils','contrail-setup'],
  pip_install    => ['ecdsa-0.10','Fabric-1.7.0'],
  responsefile   => 'contrail.preseed',
}
