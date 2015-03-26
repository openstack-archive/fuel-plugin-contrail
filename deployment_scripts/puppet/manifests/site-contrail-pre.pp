include contrail

case $operatingsystem
  {
    Ubuntu:
      {
        $pkgs = ['python-crypto','python-netaddr','python-paramiko','ifenslave-2.6','patch',
                  'openjdk-7-jre-headless','contrail-fabric-utils','contrail-setup']
        $tzdata_ver = '2014i-0ubuntu0.14.04'
        $pip_pkgs = ['ecdsa-0.10','Fabric-1.7.0']
      }

    CentOS:
      {
        $pkgs = ['python-netaddr','python-paramiko','patch',
                  'java-1.7.0-openjdk','contrail-fabric-utils','contrail-setup']
        $tzdata_ver = present
        $pip_pkgs = ['Fabric-1.7.0']
      }
  }

class { 'contrail::network':
  node_role       => 'base-os',
  address         => $contrail::address,
  ifname          => $contrail::ifname,
  netmask         => $contrail::netmask_short,
  public_addr     => $contrail::public_addr,
  public_netmask  => $contrail::public_prefix,
  public_if       => $contrail::public_if
} ->

class { 'contrail::ssh':
  password_auth => 'yes',
  root_login => 'yes'
} ->
# Workaround for contrail shipped tzdata-java package
package { 'tzdata':
  ensure  => $tzdata_ver
} ->
class { 'contrail::package':
  install        => $pkgs,
  pip_install    => $pip_pkgs
}
