include contrail

class { contrail::packages:
  plugin_version => $contrail::plugin_version,
  install        => ['python-paramiko, contrail-fabric-utils, contrail-setup'],
}
