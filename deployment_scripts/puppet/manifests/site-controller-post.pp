include contrail

class { contrail::packages:
  install => ['python-paramiko, contrail-fabric-utils, contrail-setup'],
}
