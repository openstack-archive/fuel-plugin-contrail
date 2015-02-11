class fuel-plugin-contrail
{

#if rolee = compute
  #class {"compute-base-network":}
#if role = contrail-controller
  #class {"contrailctl-base-network":}
}
