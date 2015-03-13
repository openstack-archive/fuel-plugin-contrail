include contrail

class { 'contrail::network':
  node_role => 'compute',
  address   => $contrail::address,
  ifname    => $contrail::ifname,
  netmask   => $contrail::netmask_short,
} ->

apt::source { 'contrail-from-fuel-master':
  location    => "http://${contrail::master_ip}:8080/plugins/contrail-${contrail::plugin_version}/repositories/ubuntu/",
  release     => '',
  repos       => '/',
  include_src => false,
} ->

class { 'contrail::package':
  install => 'contrail-openstack-vrouter',
  remove  => ['openvswitch-common','openvswitch-datapath-lts-saucy-dkms','openvswitch-switch',
              'nova-network','nova-api'],
} ->

class { 'contrail::config':
  node_role => $contrail::node_role,
} ->

class { 'contrail::provision':
  node_role => $contrail::node_role,
}
