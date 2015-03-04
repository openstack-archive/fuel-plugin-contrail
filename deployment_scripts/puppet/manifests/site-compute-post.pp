include contrail

class { 'contrail::network':
  node_role   => 'compute',
  address     => $contrail::address,
  ifname      => $contrail::ifname,
  netmask     => $contrail::netmask_short,
} ->

class { 'apt': disable_keys => true } ->

apt::source { 'contrail-from-fuel-master':
  location     => "http://${contrail::master_ip}:8080/contrail-${contrail::plugin_version}/repositories/ubuntu/",
  release      => '',
  repos        => '/',
  include_src  => false,
} ->

class { contrail::packages:
  install        => 'contrail-openstack-vrouter',
  remove         => ['openvswitch-common','openvswitch-datapath-lts-saucy-dkms','openvswitch-switch',
                    'nova-network','nova-api'],
}
