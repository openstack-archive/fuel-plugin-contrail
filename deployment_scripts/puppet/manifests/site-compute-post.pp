include contrail

class { 'contrail::network':
  node_role   => 'compute',
  node_ip     => $contrail::node_ip,
  ifname      => $contrail::ifname,
  cidr        => $contrail::cidr,
} ->

class { contrail::packages:
  install => 'contrail-openstack-vrouter',
  remove  => ['openvswitch-common','openvswitch-datapath-lts-saucy-dkms','openvswitch-switch',
             'nova-network','nova-api'],
}