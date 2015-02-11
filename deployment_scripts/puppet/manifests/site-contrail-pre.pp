class { contrail::packages:
  install => ['python-crypto','python-netaddr','python-paramiko',
  'contrail-fabric-utils','contrail-setup'],
  responsefile => 'contrail.preseed',
}

include contrail::contrailctl-base-network
