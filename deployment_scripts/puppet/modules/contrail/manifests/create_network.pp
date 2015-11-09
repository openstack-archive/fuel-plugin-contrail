#Not a docstring
define contrail::create_network (
  $netdata,
  $tenant_name   = 'admin',
  )
{

  if $netdata['L3']['floating'] {
    $alloc = split($netdata['L3']['floating'], ':')
    $allocation_pools = "start=${alloc[0]},end=${alloc[1]}"
  }

  notify {"${name} ::: router_ext ${netdata['L2']['router_ext']}":}
  notify {"${name} ::: tenant ${netdata['tenant']}":}
  notify {"${name} ::: shared ${netdata['shared']}":}

  neutron_network { $name:
    ensure          => present,
    router_external => $netdata['L2']['router_ext'],
    tenant_name     => $tenant_name,
    shared          => $netdata['shared']
  }

  neutron_subnet { "${name}__subnet":
    ensure           => present,
    cidr             => $netdata['L3']['subnet'],
    network_name     => $name,
    tenant_name      => $tenant_name,
    gateway_ip       => $netdata['L3']['gateway'],
    enable_dhcp      => $netdata['L3']['enable_dhcp'],
    dns_nameservers  => $netdata['L3']['nameservers'],
    allocation_pools => $allocation_pools,
  }
}
