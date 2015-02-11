include contrail

class { 'contrail::network':
  node_role   => 'base-os',
  address     => $contrail::address,
  ifname      => $contrail::ifname,
  netmask     => $contrail::netmask_short,
} ->

class { contrail::ssh:
  password_auth => 'yes',
} ->

class { contrail::packages:
  install        => ['python-crypto','python-netaddr','python-paramiko',
                    'contrail-fabric-utils','contrail-setup'],
  pip_install    => ['ecdsa-0.10','Fabric-1.7.0'],
  responsefile   => 'contrail.preseed',
  plugin_version => $contrail::plugin_version,
  master_ip      => $contrail::master_ip
}
