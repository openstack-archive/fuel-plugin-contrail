# Define to delete PCS resources
define contrail::pcs_delete_resource {
  exec { "Delete-pcs-resource-${name}":
    command => "/usr/sbin/pcs resource delete clone_p_${name}",
    returns => [0,1],
  }
}