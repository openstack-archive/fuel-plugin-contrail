include contrail

class { 'contrail::network':
  node_role   => 'compute',
  address     => $contrail::address,
  ifname      => $contrail::ifname,
  netmask     => $contrail::netmask_short,
} ->

class { contrail::packages:
  plugin_version => $contrail::plugin_version,
  install        => 'contrail-openstack-vrouter',
  remove         => ['openvswitch-common','openvswitch-datapath-lts-saucy-dkms','openvswitch-switch',
                    'nova-network','nova-api'],
  master_ip      => $contrail::master_ip
}
