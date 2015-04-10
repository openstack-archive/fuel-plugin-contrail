include contrail

if $contrail::node_name =~ /^contrail.\d+$/ {

case $operatingsystem
  {
    Ubuntu:
      {
        $pkgs = ['python-crypto','python-netaddr','python-paramiko','ifenslave-2.6','patch',
                  'openjdk-7-jre-headless','contrail-fabric-utils','contrail-setup']
        $pip_pkgs = ['ecdsa-0.10','Fabric-1.7.0']
        }
    CentOS:
      {
        $pkgs = ['python-netaddr','python-paramiko','patch',
                  'java-1.7.0-openjdk','contrail-fabric-utils','contrail-setup']
        $pip_pkgs = ['Fabric-1.7.0']
      }
  }

class { 'contrail::network':
  node_role       => 'base-os',
  address         => $contrail::address,
  ifname          => $contrail::ifname,
  netmask         => $contrail::netmask_short,
  public_addr     => $contrail::public_addr,
  public_netmask  => $contrail::public_netmask,
  public_if       => $contrail::public_if,
  public_gw       => $contrail::public_gw
} ->

class { 'contrail::ssh':
  password_auth => 'yes',
  root_login => 'yes'
} ->
class { 'contrail::package':
  install        => $pkgs,
  pip_install    => $pip_pkgs,
}

}