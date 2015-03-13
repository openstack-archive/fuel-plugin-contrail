class contrail::provision ()
{
  run_fabric { 'prov_control_bgp': } ->
  run_fabric { 'prov_external_bgp': } ->
  run_fabric { 'prov_metadata_services': } ->
  run_fabric { 'prov_encap_type': }
}

