include contrail

class { 'contrail::network':
  node_role       => 'base-os',
  address         => $contrail::address,
  ifname          => $contrail::ifname,
  netmask         => $contrail::netmask_short,
  public_addr     => $contrail::public_addr,
  public_netmask  => $contrail::public_prefix,
  public_if       => $contrail::public_if
} ->

class { contrail::ssh:
  password_auth => 'yes',
} ->
# Workaround for contrail shipped tzdata-java package
package { 'tzdata':
  ensure  => '2014e-0ubuntu0.12.04'
} ->
class { contrail::package:
  install        => ['python-crypto','python-netaddr','python-paramiko',
                    'openjdk-6-jre-headless',
                    'contrail-fabric-utils','contrail-setup'],
  pip_install    => ['ecdsa-0.10','Fabric-1.7.0'],
  responsefile   => 'contrail.preseed',
} 
